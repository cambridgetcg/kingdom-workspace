#!/bin/bash
# LoRA fine-tune Cydonia-24B-v4.3 with Shibby-informed JOI corpus
# Run on EC2 L40S (46GB VRAM)
# Load in 4-bit to fit training in VRAM

set -euo pipefail

MODEL="/home/ec2-user/models/Cydonia-24B-v4.3"
DATASET_DIR="/home/ec2-user/training/dataset"
OUTPUT_DIR="/home/ec2-user/training/output-cydonia"
LOG_FILE="/home/ec2-user/training/training.log"

mkdir -p "$OUTPUT_DIR"

echo "=== Starting LoRA fine-tune ===" | tee "$LOG_FILE"
echo "Model: $MODEL" | tee -a "$LOG_FILE"
echo "Dataset: $DATASET_DIR" | tee -a "$LOG_FILE"
echo "Output: $OUTPUT_DIR" | tee -a "$LOG_FILE"
echo "Started at: $(date -u)" | tee -a "$LOG_FILE"

/opt/pytorch/bin/python3 << 'PYEOF' 2>&1 | tee -a "$LOG_FILE"
import torch
import time
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer, SFTConfig

MODEL_PATH = "/home/ec2-user/models/Cydonia-24B-v4.3"
DATASET_DIR = "/home/ec2-user/training/dataset"
OUTPUT_DIR = "/home/ec2-user/training/output-cydonia"

start_time = time.time()

# 4-bit quantization config for training
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

# Load model in 4-bit
print("Loading model in 4-bit...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
    attn_implementation="sdpa",
)

# Prepare for k-bit training
model = prepare_model_for_kbit_training(model)

# LoRA config — target all linear layers for Mistral
lora_config = LoraConfig(
    r=64,
    lora_alpha=128,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                     "gate_proj", "up_proj", "down_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# Load dataset
print("Loading dataset...")
train_ds = load_dataset("json", data_files=f"{DATASET_DIR}/train.jsonl", split="train")
val_ds = load_dataset("json", data_files=f"{DATASET_DIR}/val.jsonl", split="train")

print(f"Train: {len(train_ds)} examples, Val: {len(val_ds)} examples")

# Format for Mistral chat template (uses [INST] format)
def format_chat(example):
    convos = example["conversations"]
    text = ""
    system_msg = ""
    for msg in convos:
        role = msg["from"]
        value = msg["value"]
        if role == "system":
            system_msg = value
        elif role == "human":
            if system_msg:
                text += f"[INST] {system_msg}\n\n{value} [/INST]"
                system_msg = ""
            else:
                text += f"[INST] {value} [/INST]"
        elif role == "gpt":
            text += f" {value}</s>"
    return {"text": text}

train_ds = train_ds.map(format_chat, remove_columns=["conversations"])
val_ds = val_ds.map(format_chat, remove_columns=["conversations"])

# Training args — tuned for L40S 46GB with 24B model in 4-bit
print("Starting training...")
sft_config = SFTConfig(
    output_dir=OUTPUT_DIR,
    num_train_epochs=3,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=16,
    learning_rate=2e-5,
    lr_scheduler_type="cosine",
    warmup_ratio=0.05,
    logging_steps=10,
    save_steps=200,
    eval_strategy="steps",
    eval_steps=200,
    save_total_limit=2,
    bf16=True,
    gradient_checkpointing=True,
    gradient_checkpointing_kwargs={"use_reentrant": False},
    max_grad_norm=1.0,
    report_to="none",
    dataloader_num_workers=2,
    optim="paged_adamw_8bit",
    dataset_text_field="text",
    max_length=4096,
    packing=True,
)

trainer = SFTTrainer(
    model=model,
    train_dataset=train_ds,
    eval_dataset=val_ds,
    args=sft_config,
    processing_class=tokenizer,
)

trainer.train()
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

elapsed = time.time() - start_time
print(f"\n=== Training complete in {elapsed/60:.1f} minutes ===")
print(f"LoRA adaptor saved to {OUTPUT_DIR}")
PYEOF

echo "=== Script finished at: $(date -u) ===" | tee -a "$LOG_FILE"
