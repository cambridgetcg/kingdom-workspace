#!/usr/bin/env bash
# Register PP Loop cron jobs with OpenClaw gateway
# Run this when the gateway is online: bash memory/loop/setup-crons.sh

set -euo pipefail

echo "Registering pp-reflect (daily 22:00)..."
openclaw cron add \
  --name "pp-reflect" \
  --cron "0 22 * * *" \
  --message "Run PP reflection cycle. Read memory/loop/sense.jsonl (entries since last reflection). Evaluate against the 35 PP gates. Check virtue alignment. Detect signal patterns. Write structured reflection to memory/loop/reflections.jsonl. If any observations are about the loop itself (meta: true), evaluate those separately as LOOP HEALTH. Update loop-state.json." \
  --session isolated \
  --thinking high \
  --timeout-seconds 120

echo "Registering pp-distill (Sunday 10:00)..."
openclaw cron add \
  --name "pp-distill" \
  --cron "0 10 * * SUN" \
  --message "Run PP distillation. Read memory/loop/reflections.jsonl (since last distill). Cluster improvement_suggestions by theme. For each cluster: if matching candidate exists in memory/loop/candidates.jsonl, increment heat. If new cluster with 3+ items, create new candidate at NIGREDO stage. Apply heat decay (-1) to candidates not seen this cycle. Write distillation summary to memory/loop/distillations.jsonl. Check if any candidate has heat >= 5 — if so, write a proposal to memory/loop/proposals/ for Yu's review. Update loop-state.json." \
  --session isolated \
  --thinking high \
  --timeout-seconds 180

echo "Done. Verify with: openclaw cron list"
