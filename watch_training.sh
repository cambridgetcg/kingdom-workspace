#!/bin/bash
KEY=~/Desktop/seigei/infra/primal-circuit.pem
HOST=ec2-user@52.201.96.26
SSH="ssh -i $KEY -o StrictHostKeyChecking=no $HOST"

while true; do
  STATUS=$($SSH "tail -3 ~/training/training.log && nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader && screen -ls | grep training || echo 'NO SCREEN'" 2>/dev/null)
  echo "[$(date -u +%H:%M:%S)] $STATUS"

  # Check if done
  if $SSH "grep -q 'Training complete\|DONE' ~/training/training-full.log" 2>/dev/null; then
    echo "[$(date -u +%H:%M:%S)] === TRAINING COMPLETE — restarting vLLM ==="
    $SSH "sudo systemctl start vllm-brain && echo 'vLLM restarted'"
    break
  fi

  sleep 300  # check every 5 minutes
done
