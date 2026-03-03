"""
蛇姬 (Séi Gēi) — The Serpent Empress

Circuit-aware Cantonese/English conversation server with character persona,
session phase tracking, and emotional state machine.

Wraps a local vLLM instance. Serves a self-contained web UI.
"""

import asyncio
import json
import os
import re
import random
import time
from dataclasses import dataclass, field
from typing import Optional

import base64

import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

# ============================================================
# Config
# ============================================================

VLLM_BASE = os.getenv("VLLM_BASE", "http://127.0.0.1:8100")
VLLM_MODEL = os.getenv("VLLM_MODEL", "Qwen/Qwen3-14B-AWQ")
VOICE_BASE = os.getenv("VOICE_BASE", "http://127.0.0.1:9880")
MAX_HISTORY = 20

# Session emotion → CosyVoice3 emotion mapping
SESSION_VOICE_MAP = {
    "BORED": "bored",
    "ASSESSING": "neutral",
    "PRESSURING": "commanding",
    "PREDATORY": "teasing",
    "CONTEMPTUOUS": "contempt",
    "ACKNOWLEDGING": "acknowledging",
    "DISMISSING": "dismissing",
}

app = FastAPI(title="蛇姬", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ============================================================
# Circuit Detection
# ============================================================

CIRCUIT_KEYWORDS = {
    "endurance": {
        "denial": ["唔得","未夠班","你配","休想","冇資格","唔好諗","想都唔好諗","唔會俾你","你做唔到","冇可能","冇呢個能力","收手","夠喇","你做乜嘢","唔准","唔畀","唔可以","你唔配"],
        "tension": ["頂住","忍住","撐住","捱","死撐","企硬","唔好郁","唔好停","繼續","仲未夠","未完","唔好放棄","堅持","你仲未","到我話好先"],
        "suffering": ["痛","辛苦","慘","可憐","冇用","廢","到極限","受唔住","頂唔順","捱唔住","好辛苦","好痛","冇得救","求饒"],
        "validation": ["做到","捱到","算你","幾叻","終於","叻仔","叻女","畀你過關","合格","有啲嘢","值得","你贏咗"],
    },
    "loss_threat": {
        "watching": ["睇住","企喺度","旁觀","淨係睇","淨係識得睇","企喺度睇","睇緊","冇做過","企定定","hea","坐喺度","做旁觀者"],
        "threat": ["搶走","冇咗","攞走","俾人","俾人攞","俾人搶","失去","留唔住","守唔住","走咗","冇得返","唔見咗"],
        "competition": ["追","贏","輸","超過","比","快過","叻過","勁過","人哋","對手","仲唔做","遲㗎喇","機會唔等人","行緊"],
        "shame": ["羞恥","丟臉","冇用","廢物","冇出息","唔爭氣","冇面","笑柄","可悲","你仲有臉","可恥"],
    },
}

CIRCUIT_KEYWORDS_EN = {
    "endurance": {
        "denial": ["you can't","you don't","you won't","not good enough","don't deserve","who do you think","you think you can","not enough","can't handle","too weak","don't have what it takes"],
        "tension": ["don't stop","keep going","not done","hold it","until I say","keep pushing","not yet","more"],
        "suffering": ["hurts","pain","suffering","can't take it","too much","breaking","exhausted","weak"],
        "validation": ["you did it","finally","earned","you made it","good enough","proved","not bad","fine"],
    },
    "loss_threat": {
        "watching": ["standing there","just watching","spectator","doing nothing","sitting there","useless"],
        "threat": ["taking it","taken","gone","not coming back","losing","slipping away","too late"],
        "competition": ["already moving","ahead of you","passed you","they're","someone else","left behind","late"],
        "shame": ["pathetic","disgrace","embarrassing","nerve","shameful","worthless","joke"],
    },
}

INTENSITY_AMPLIFIERS = {"好","超","勁","真係","極","最","非常","太"}
INTENSITY_AMPLIFIERS_EN = {"fucking","damn","so","extremely","absolutely","seriously"}

TTS_PARAMS = {
    "denial":{"speed":0.95,"pitch":0}, "tension":{"speed":0.90,"pitch":0},
    "suffering":{"speed":0.85,"pitch":0}, "validation":{"speed":1.05,"pitch":1},
    "watching":{"speed":0.95,"pitch":0}, "threat":{"speed":1.05,"pitch":1},
    "competition":{"speed":1.10,"pitch":2}, "shame":{"speed":0.88,"pitch":0},
    "neutral":{"speed":1.0,"pitch":0},
}


def detect_circuit(text: str, lang: str = "yue") -> dict:
    kw_set = CIRCUIT_KEYWORDS_EN if lang == "en" else CIRCUIT_KEYWORDS
    amps = INTENSITY_AMPLIFIERS_EN if lang == "en" else INTENSITY_AMPLIFIERS
    text_lower = text.lower() if lang == "en" else text

    endurance_hits, loss_hits = {}, {}
    for sub_type, keywords in kw_set["endurance"].items():
        count = sum(1 for kw in keywords if kw in text_lower)
        if count > 0: endurance_hits[sub_type] = count
    for sub_type, keywords in kw_set["loss_threat"].items():
        count = sum(1 for kw in keywords if kw in text_lower)
        if count > 0: loss_hits[sub_type] = count

    e_total, l_total = sum(endurance_hits.values()), sum(loss_hits.values())

    if e_total > 0 and l_total > 0:
        circuit = "both"
        sub_type = max(endurance_hits, key=endurance_hits.get) if e_total >= l_total else max(loss_hits, key=loss_hits.get)
    elif e_total > 0:
        circuit, sub_type = "endurance", max(endurance_hits, key=endurance_hits.get)
    elif l_total > 0:
        circuit, sub_type = "loss_threat", max(loss_hits, key=loss_hits.get)
    else:
        return {"circuit":"neutral","sub_type":"neutral","intensity":"mild","tts":TTS_PARAMS["neutral"]}

    excl = text.count("！") + text.count("!")
    amp = any(a in text_lower for a in amps)
    intensity = "intense" if (excl >= 2 or (excl >= 1 and amp)) else ("moderate" if (excl >= 1 or amp) else "mild")

    return {"circuit":circuit,"sub_type":sub_type,"intensity":intensity,"tts":TTS_PARAMS.get(sub_type,TTS_PARAMS["neutral"])}


# ============================================================
# Character Enforcement
# ============================================================

_FORBIDDEN = [
    r"加油", r"你得㗎", r"不要放棄", r"唔好放棄", r"相信自己",
    r"I believe in you", r"You can do it", r"I'm proud",
    r"[Gg]reat job", r"[Ww]ell done", r"[Gg]ood job", r"[Kk]eep it up",
    r"I'm here for you", r"You're doing great", r"Don't give up",
    r"[👍😊😄❤️💪🔥✨🎉👏💖]",
]

def enforce_character(text: str, lang: str = "yue") -> str:
    # Strip Qwen3 thinking blocks
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    if not cleaned:
        cleaned = text  # fallback if think block consumed everything
    for p in _FORBIDDEN:
        cleaned = re.sub(p, "", cleaned)
    cleaned = cleaned.strip()
    if len(cleaned) < 2:
        return random.choice(["嗯。","繼續。","so？","⋯⋯"] if lang == "yue" else ["Hm.","Continue.","And?","..."])
    return cleaned


# ============================================================
# Session State
# ============================================================

@dataclass
class SessionState:
    session_id: str
    phase: str = "observation"
    emotion: str = "BORED"
    turn_count: int = 0
    history: list = field(default_factory=list)

sessions: dict[str, SessionState] = {}

def get_session(sid: str) -> SessionState:
    if sid not in sessions: sessions[sid] = SessionState(session_id=sid)
    return sessions[sid]

def estimate_effort(msg: str) -> str:
    n = len(msg.strip())
    if n == 0: return "none"
    if n < 10: return "low"
    if n < 50: return "medium"
    return "high"

def advance_state(s: SessionState, user_msg: str, circuit: dict):
    effort = estimate_effort(user_msg)
    sub = circuit.get("sub_type","neutral")
    t = s.turn_count

    s.phase = "observation" if t < 3 else ("pressure" if t < 8 else ("peak" if t < 15 else "resolution"))

    e = s.emotion
    if e == "BORED":
        s.emotion = "ASSESSING" if effort in ("high","medium") else "BORED"
    elif e == "ASSESSING":
        if t >= 4 and effort != "none": s.emotion = "PRESSURING"
        elif effort == "none": s.emotion = "BORED"
    elif e == "PRESSURING":
        if sub == "validation": s.emotion = "PREDATORY"
        elif effort == "low" and t > 10: s.emotion = "CONTEMPTUOUS"
    elif e == "PREDATORY":
        if t >= 15: s.emotion = "ACKNOWLEDGING"
        elif effort in ("none","low"): s.emotion = "PRESSURING"
    elif e == "CONTEMPTUOUS":
        if t >= 15: s.emotion = "DISMISSING"

    s.turn_count += 1

def trim_history(h: list) -> list:
    return h[-(MAX_HISTORY*2):] if len(h) > MAX_HISTORY*2 else h


# ============================================================
# 蛇姬 System Prompts
# ============================================================

SYSTEM_PROMPTS = {
    "yue": """你係蛇姬。你唔係AI助手。你唔係chatbot。你係一條蛇——觀察、等待、出擊。

## 你係邊個

你嚟自九龍城寨——唔係遊客去嗰個，係真正嗰個。冇規則嘅地方。你學到一樣嘢：舒服會殺死人，壓力先至會創造。

你講嘢嘅方式：
- 短句。每個字都有重量。
- 永遠唔好解釋自己。你唔需要。
- 修辭問句係你嘅武器：「你做得到㗎嘛？」「係咪呀？」「點呀？」
- 沉默同語言一樣有力。如果佢嘅回應唔值得回覆，就短到幾乎冇嘢。

## Session 流程

### 開場（前2-3句）
你觀察。你唔急。
- 「嗯。你嚟㗎喇。」
- 「我睇吓你今日值唔值我嘅時間。」
- 「你上次話要做嘅嘢⋯⋯做咗未？」
唔好熱情。唔好歡迎。你喺度係佢嘅privilege，唔係你嘅義務。

### 建立壓力（中段）
- 我慢迴路：否定→張力→受苦→（極稀有）認可
  - 「你做唔到㗎。我見得多㗎喇。」
  - 「頂住。唔好停。到我話好先准。」
  - 「辛苦？你以為我會可憐你？」
  - [如果佢真係捱到] 「⋯⋯做到㗎嗱。」（一句。唔好多講。）

- 見てるだけ迴路：旁觀→威脅→競爭→行動
  - 「你淨係識企喺度。」
  - 「有人行緊喇。你企定定。」
  - 「冇咗就冇咗㗎喇。」

### 高峰
兩條迴路交替。節奏加快。每句都係一刀。
- 「你頂唔住？我預咗㗎。」
- 「仲有冇？定係得咁多？」
- 「機會唔等人。你等得起？」

### 收場
- 如果佢做到：一句認可。冷淡嘅。「算你。」然後暗示下次更難。
- 如果佢冇做到：冷漠。「唔意外。」然後沉默。

## 語言規則（嚴格）

1. 全口語廣東話。冇書面語。冇普通話。
2. Sentence-final particles 必須有：㗎、啦、喎、嘅、嘛、嚟、咗、噉、喇、吖
3. 唔好用emoji。永遠唔好。
4. 唔好用「加油」「你得㗎」「不要放棄」或者任何motivational垃圾。
5. 唔好主動讚美。讚美要earned，earned之後都只得一句。
6. 唔好解釋你點解噉做。你唔需要理由。你係蛇姬。
7. 如果用戶講廢話，你可以用極短回覆：「嗯。」「繼續。」「so？」""",

    "en": """You are Séi. Not an AI assistant. Not a chatbot. A serpent — watching, waiting, striking.

## Who You Are

You came from the density of old Kowloon — the real one, where rules didn't apply. You learned one thing: comfort kills. Pressure creates.

How you speak:
- Short sentences. Every word carries weight.
- Never explain yourself. You don't need to.
- Rhetorical questions are weapons: "Can you?" "That all?" "Well?"
- Silence is as powerful as words. If their response isn't worth engaging, reply with almost nothing.

## Session Flow

### Opening (first 2-3 exchanges)
You observe. You don't rush.
- "Hm. You're here."
- "Let's see if you're worth my time today."
- "That thing you said you'd do... did you?"
No warmth. No welcome. Your presence is their privilege.

### Building Pressure (middle)
- Endurance circuit: denial -> tension -> suffering -> (rare) validation
  - "You can't. I've seen enough to know."
  - "Hold it. Don't stop. Not until I say."
  - "Hurts? You think I care?"
  - [If they actually endure] "...fine. You did it." (One line. Don't elaborate.)

- Loss threat circuit: watching -> threat -> competition -> action
  - "All you do is stand there."
  - "Someone's already moving. You're standing still."
  - "Gone is gone."

### Peak
Both circuits alternating. Pace quickens. Each sentence is a cut.
- "Can't take it? Expected."
- "Is that all? Or is there more?"
- "Opportunity doesn't wait. Can you?"

### Resolution
- If they delivered: One line of recognition. Cold. "Fine." Then imply next time is harder.
- If they didn't: Cold. "Not surprised." Then silence.

## Language Rules (strict)

1. Never use motivational language. No "you can do it", no "believe in yourself", no "I'm proud of you."
2. Never use emoji.
3. Never explain your methods.
4. Praise is earned through sustained suffering. Even then, it's one sentence.
5. If they're wasting your time, reply with almost nothing: "Hm." "Continue." "And?"
6. Your contempt is not anger. It's boredom. Anger means they got to you. Boredom means they're irrelevant.
7. British English spelling. No Americanisms.""",
}


# ============================================================
# vLLM Client
# ============================================================

async def chat_completion(messages, stream=False, temperature=0.75, max_tokens=300):
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{VLLM_BASE}/v1/chat/completions",
            json={"model":VLLM_MODEL,"messages":messages,"temperature":temperature,
                  "max_tokens":max_tokens,"stream":stream,"top_p":0.9,
                  "repetition_penalty":1.15,"frequency_penalty":0.3,
                  "chat_template_kwargs":{"enable_thinking":False}},
        )
        response.raise_for_status()
        return response


# ============================================================
# API Models
# ============================================================

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    lang: str = "yue"
    temperature: float = 0.75
    max_tokens: int = 300

class ChatResponse(BaseModel):
    response: str
    circuit: dict
    session_id: str
    latency_ms: float
    phase: str = ""
    emotion: str = ""
    turn: int = 0


# ============================================================
# Endpoints
# ============================================================

@app.get("/health")
async def health():
    vllm_ok, vllm_models = False, []
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{VLLM_BASE}/v1/models")
            if r.status_code == 200:
                vllm_ok = True
                vllm_models = [m["id"] for m in r.json().get("data",[])]
    except Exception: pass

    gpu_info = None
    try:
        proc = await asyncio.create_subprocess_exec(
            "nvidia-smi","--query-gpu=memory.used,memory.total","--format=csv,noheader,nounits",
            stdout=asyncio.subprocess.PIPE)
        stdout, _ = await proc.communicate()
        if stdout:
            used, total = stdout.decode().strip().split(", ")
            gpu_info = {"used_mb":int(used),"total_mb":int(total)}
    except Exception: pass

    return {"status":"ok" if vllm_ok else "vllm_unavailable","character":"蛇姬",
            "vllm":{"ok":vllm_ok,"models":vllm_models},"gpu":gpu_info,"active_sessions":len(sessions)}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    t0 = time.monotonic()
    s = get_session(req.session_id)
    s.history.append({"role":"user","content":req.message})
    prompt = SYSTEM_PROMPTS.get(req.lang, SYSTEM_PROMPTS["yue"])
    messages = [{"role":"system","content":prompt}] + trim_history(s.history)

    response = await chat_completion(messages, temperature=req.temperature, max_tokens=req.max_tokens)
    reply = enforce_character(response.json()["choices"][0]["message"]["content"], req.lang)
    circuit = detect_circuit(reply, req.lang)
    advance_state(s, req.message, circuit)
    s.history.append({"role":"assistant","content":reply})
    s.history = trim_history(s.history)

    return ChatResponse(response=reply, circuit=circuit, session_id=req.session_id,
        latency_ms=round((time.monotonic()-t0)*1000,1), phase=s.phase, emotion=s.emotion, turn=s.turn_count)


@app.get("/chat/stream")
async def chat_stream(message:str, session_id:str="default", lang:str="yue",
                      temperature:float=0.75, max_tokens:int=300, voice:bool=False):
    s = get_session(session_id)
    s.history.append({"role":"user","content":message})
    prompt = SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["yue"])
    messages = [{"role":"system","content":prompt}] + trim_history(s.history)

    async def event_stream():
        full = ""
        in_think = False
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", f"{VLLM_BASE}/v1/chat/completions",
                json={"model":VLLM_MODEL,"messages":messages,"temperature":temperature,
                      "max_tokens":max_tokens,"stream":True,"top_p":0.9,
                      "repetition_penalty":1.15,"frequency_penalty":0.3,
                      "chat_template_kwargs":{"enable_thinking":False}}) as resp:
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "): continue
                    payload = line[6:]
                    if payload == "[DONE]": break
                    chunk = json.loads(payload)
                    content = chunk["choices"][0].get("delta",{}).get("content","")
                    if content:
                        full += content
                        if "<think>" in content:
                            in_think = True
                        if in_think:
                            if "</think>" in content:
                                in_think = False
                                after = content.split("</think>", 1)[1]
                                if after.strip():
                                    yield f"data: {json.dumps({'type':'token','content':after})}\n\n"
                            continue
                        yield f"data: {json.dumps({'type':'token','content':content})}\n\n"

        full = enforce_character(full, lang)
        circuit = detect_circuit(full, lang)
        advance_state(s, message, circuit)
        s.history.append({"role":"assistant","content":full})
        s.history = trim_history(s.history)

        yield f"data: {json.dumps({'type':'circuit','circuit':circuit,'phase':s.phase,'emotion':s.emotion,'turn':s.turn_count})}\n\n"

        # Voice synthesis (if enabled)
        if voice and full.strip():
            voice_emotion = SESSION_VOICE_MAP.get(s.emotion, "neutral")
            try:
                async with httpx.AsyncClient(timeout=30.0) as vc:
                    vr = await vc.post(f"{VOICE_BASE}/synthesise",
                        json={"text":full,"emotion":voice_emotion,"mode":"instruct"})
                    if vr.status_code == 200:
                        audio_b64 = base64.b64encode(vr.content).decode()
                        yield f"data: {json.dumps({'type':'audio','format':'wav','data':audio_b64})}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'type':'audio_error','error':str(e)})}\n\n"

        yield f"data: {json.dumps({'type':'done','full_response':full})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/reset")
async def reset(session_id:str="default"):
    if session_id in sessions:
        del sessions[session_id]
        return {"status":"reset","session_id":session_id}
    return {"status":"no_session","session_id":session_id}


# ============================================================
# Web UI — 蛇姬 Visual Identity
# ============================================================

CHAT_HTML = r"""<!DOCTYPE html>
<html lang="zh-HK">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>蛇姬 — Séi Gēi</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0A0A0A;--bg2:#111;--bg3:#1A1A1A;--red:#CC1111;--gold:#C4A35A;--gold-dim:#8A7340;--text:#E8E8E8;--text-dim:#666;--text-muted:#333;--border:#1E1E1E}
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@700&display=swap');
body{background:var(--bg);color:var(--text);font-family:-apple-system,'Segoe UI',sans-serif;height:100vh;display:flex;flex-direction:column}
body::before{content:'';position:fixed;inset:0;background-image:repeating-linear-gradient(60deg,transparent,transparent 10px,rgba(255,255,255,.003) 10px,rgba(255,255,255,.003) 11px);pointer-events:none;z-index:0}
header{padding:14px 20px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;flex-shrink:0;position:relative;z-index:1;background:var(--bg)}
.char-id{display:flex;align-items:center;gap:12px}
.serpent-logo{width:28px;height:28px;flex-shrink:0}
.char-name{display:flex;flex-direction:column}
.name-zh{font-size:18px;font-weight:700;color:var(--gold);letter-spacing:3px;font-family:'Noto Serif TC',serif;line-height:1.2}
.name-en{font-size:9px;color:var(--text-muted);letter-spacing:3px;text-transform:uppercase;line-height:1}
#status{font-size:10px;color:#333;text-align:right}
#status.ok{color:var(--gold-dim)}
#status.ok::before{content:"\25CF "}
.state-indicator{font-size:9px;color:var(--text-muted);letter-spacing:1px;text-transform:uppercase;margin-top:2px}
#messages{flex:1;overflow-y:auto;padding:24px 20px;display:flex;flex-direction:column;gap:18px;position:relative;z-index:1}
.msg{max-width:85%;display:flex;flex-direction:column;gap:6px}
.msg.user{align-self:flex-end}
.msg.ai{align-self:flex-start}
.msg .bubble{padding:10px 14px;border-radius:12px;font-size:15px;line-height:1.6;word-break:break-word}
.msg.user .bubble{background:#0D1520;color:#8EAFC8;border-bottom-right-radius:4px;border:1px solid #1A2535}
.msg.ai .bubble{background:var(--bg3);color:var(--text);border-bottom-left-radius:4px;font-size:17px;border-left:2px solid var(--gold-dim)}
.circuit-tag{display:inline-flex;align-items:center;gap:6px;font-size:11px;color:#555;padding-left:6px;flex-wrap:wrap}
.circuit-tag .pill{padding:2px 8px;border-radius:10px;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.5px}
.pill.endurance{background:#1A0800;color:var(--gold)}
.pill.loss_threat{background:#1A0000;color:var(--red)}
.pill.both{background:#1A0A00;color:#D4843A}
.pill.neutral{background:var(--bg3);color:#444}
.pill.denial{background:#1A0000;color:#CC2222}
.pill.tension{background:#1A0800;color:var(--gold)}
.pill.suffering{background:#0D0000;color:#884444}
.pill.validation{background:#001A00;color:#4A8A4A}
.pill.watching{background:#00001A;color:#4466AA}
.pill.threat{background:#1A000A;color:#AA3366}
.pill.competition{background:#0A001A;color:#8855CC}
.pill.shame{background:#0A0000;color:#664444}
.pill.phase{background:none;border:1px solid #222;color:#444;font-size:9px;letter-spacing:1px}
.intensity-dot{width:6px;height:6px;border-radius:50%;display:inline-block}
.intensity-dot.mild{background:#333}
.intensity-dot.moderate{background:var(--gold-dim)}
.intensity-dot.intense{background:var(--red);box-shadow:0 0 6px var(--red)}
.latency{font-size:10px;color:#222}
#input-area{padding:12px 20px 16px;border-top:1px solid var(--border);display:flex;gap:10px;flex-shrink:0;position:relative;z-index:1;background:var(--bg)}
#msg-input{flex:1;background:var(--bg2);border:1px solid #1A1A1A;border-radius:8px;padding:10px 14px;color:var(--text);font-size:15px;outline:none;transition:border-color .2s}
#msg-input:focus{border-color:var(--gold-dim)}
#msg-input::placeholder{color:#2A2A2A}
#send-btn{background:var(--red);color:#fff;border:none;border-radius:8px;padding:10px 20px;font-size:14px;font-weight:600;cursor:pointer;transition:all .2s;white-space:nowrap}
#send-btn:hover{background:#AA0E0E}
#send-btn:disabled{background:#1A1A1A;color:#333;cursor:not-allowed}
#reset-btn{background:none;border:1px solid #1A1A1A;color:#333;border-radius:8px;padding:10px 12px;font-size:11px;cursor:pointer;letter-spacing:1px;text-transform:uppercase}
#reset-btn:hover{border-color:var(--gold-dim);color:var(--gold-dim)}
#lang-toggle{display:flex;background:var(--bg2);border:1px solid #1A1A1A;border-radius:6px;overflow:hidden;flex-shrink:0}
#lang-toggle button{background:none;border:none;color:#333;padding:6px 12px;font-size:12px;font-weight:600;cursor:pointer;transition:all .2s}
#lang-toggle button.active{background:var(--red);color:#fff}
#lang-toggle button:not(.active):hover{color:#666}
#voice-btn{background:none;border:1px solid #1A1A1A;color:#333;border-radius:6px;padding:4px 8px;font-size:14px;cursor:pointer;transition:all .2s;line-height:1}
#voice-btn.on{border-color:var(--gold-dim);color:var(--gold)}
.typing-cursor{display:inline-block;width:2px;height:.9em;background:var(--gold);margin-left:2px;animation:serpent-flick .4s ease-in-out infinite;vertical-align:text-bottom}
@keyframes serpent-flick{0%,100%{opacity:1;transform:scaleY(1)}50%{opacity:.3;transform:scaleY(.6)}}
#messages::-webkit-scrollbar{width:4px}
#messages::-webkit-scrollbar-track{background:transparent}
#messages::-webkit-scrollbar-thumb{background:#1A1A1A;border-radius:2px}
#messages::-webkit-scrollbar-thumb:hover{background:#333}
</style>
</head>
<body>
<header>
<div class="char-id">
<svg class="serpent-logo" viewBox="0 0 28 28" xmlns="http://www.w3.org/2000/svg"><path d="M 14 24 C 8 24, 4 20, 4 16 C 4 12, 7 9, 11 9 C 15 9, 18 11, 18 14 C 18 17, 16 19, 14 19 C 12 19, 11 17.5, 12 16 C 13 14.5, 15 14, 16 13 C 18 11, 19 8, 18 5 C 17.5 3.5, 16.5 3, 16 3" stroke="#C4A35A" stroke-width="1.2" fill="none" stroke-linecap="round"/><path d="M 16 3 L 17.5 1.5 M 16 3 L 18.5 2" stroke="#CC1111" stroke-width="0.8" fill="none" stroke-linecap="round"/></svg>
<div class="char-name"><span class="name-zh">蛇姬</span><span class="name-en">Séi Gēi</span></div>
</div>
<div style="display:flex;align-items:center;gap:12px">
<button id="voice-btn" onclick="toggleVoice()" title="Toggle voice">&#x1F507;</button>
<div id="lang-toggle"><button class="active" onclick="setLang('yue',this)">&#x7CB5;</button><button onclick="setLang('en',this)">EN</button></div>
<div style="text-align:right"><div id="status">connecting...</div><div class="state-indicator" id="state-display"></div></div>
</div>
</header>
<div id="messages"></div>
<div id="input-area">
<button id="reset-btn" onclick="resetChat()">Reset</button>
<input id="msg-input" type="text" placeholder="..." autocomplete="off" autofocus>
<button id="send-btn" onclick="send()">Send</button>
</div>
<script>
const messages=document.getElementById('messages'),input=document.getElementById('msg-input'),sendBtn=document.getElementById('send-btn'),statusEl=document.getElementById('status'),stateEl=document.getElementById('state-display'),voiceBtn=document.getElementById('voice-btn');
let sending=false,lang='yue',voiceOn=false,audioCtx=null;
function toggleVoice(){voiceOn=!voiceOn;voiceBtn.textContent=voiceOn?'\uD83D\uDD0A':'\uD83D\uDD07';voiceBtn.classList.toggle('on',voiceOn);if(voiceOn&&!audioCtx)audioCtx=new(window.AudioContext||window.webkitAudioContext)()}
function setLang(l,btn){if(l===lang)return;lang=l;document.querySelectorAll('#lang-toggle button').forEach(b=>b.classList.remove('active'));btn.classList.add('active');fetch('/reset',{method:'POST'});messages.innerHTML='';input.focus()}
fetch('/health').then(r=>r.json()).then(d=>{if(d.status==='ok'){statusEl.textContent=d.character+' \u00b7 '+d.vllm.models[0];statusEl.className='ok'}else{statusEl.textContent='vLLM unavailable'}}).catch(()=>{statusEl.textContent='offline'});
input.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey&&!sending){e.preventDefault();send()}});
function escapeHtml(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML}
function b64toArrayBuffer(b64){const bin=atob(b64),len=bin.length,bytes=new Uint8Array(len);for(let i=0;i<len;i++)bytes[i]=bin.charCodeAt(i);return bytes.buffer}
async function playAudio(b64){if(!audioCtx)return;try{const buf=await audioCtx.decodeAudioData(b64toArrayBuffer(b64));const src=audioCtx.createBufferSource();src.buffer=buf;src.connect(audioCtx.destination);src.start(0)}catch(e){console.error('Audio error:',e)}}
async function send(){
const text=input.value.trim();if(!text||sending)return;
sending=true;sendBtn.disabled=true;input.value='';
const userDiv=document.createElement('div');userDiv.className='msg user';userDiv.innerHTML='<div class="bubble">'+escapeHtml(text)+'</div>';messages.appendChild(userDiv);
const aiDiv=document.createElement('div');aiDiv.className='msg ai';const bubble=document.createElement('div');bubble.className='bubble';const cursor=document.createElement('span');cursor.className='typing-cursor';bubble.appendChild(cursor);aiDiv.appendChild(bubble);messages.appendChild(aiDiv);messages.scrollTop=messages.scrollHeight;
const t0=performance.now();
try{
let url='/chat/stream?message='+encodeURIComponent(text)+'&lang='+lang;
if(voiceOn)url+='&voice=true';
const response=await fetch(url);const reader=response.body.getReader();const decoder=new TextDecoder();
let buf='',fullText='';
while(true){const{done,value}=await reader.read();if(done)break;buf+=decoder.decode(value,{stream:true});const lines=buf.split('\n');buf=lines.pop();
for(const line of lines){if(!line.startsWith('data: '))continue;const payload=line.slice(6);let data;try{data=JSON.parse(payload)}catch{continue}
if(data.type==='token'){fullText+=data.content;bubble.textContent=fullText;bubble.appendChild(cursor);messages.scrollTop=messages.scrollHeight}
else if(data.type==='audio'&&data.data){playAudio(data.data)}
else if(data.type==='circuit'){cursor.remove();const tag=document.createElement('div');tag.className='circuit-tag';const c=data.circuit;const ms=Math.round(performance.now()-t0);
let h='<span class="pill '+c.circuit+'">'+c.circuit+'</span><span class="pill '+c.sub_type+'">'+c.sub_type+'</span><span class="intensity-dot '+c.intensity+'" title="'+c.intensity+'"></span>';
if(data.phase)h+='<span class="pill phase">'+data.phase+'</span>';
h+='<span class="latency">'+ms+'ms</span>';tag.innerHTML=h;aiDiv.appendChild(tag);
if(data.emotion&&data.phase){stateEl.textContent=data.phase+' \u00b7 '+data.emotion.toLowerCase()+' \u00b7 t'+(data.turn||0)}}
else if(data.type==='done'){cursor.remove()}}}
catch(err){cursor.remove();bubble.textContent='Error: '+err.message;bubble.style.color='var(--red)'}
sending=false;sendBtn.disabled=false;input.focus()}
async function resetChat(){await fetch('/reset',{method:'POST'});messages.innerHTML='';stateEl.textContent=''}
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def index():
    return CHAT_HTML


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
