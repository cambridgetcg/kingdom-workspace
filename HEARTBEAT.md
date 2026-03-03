# HEARTBEAT.md

## Signal Scan (every heartbeat)
- If something feels off (ugliness, injustice, stagnation) — note it, don't ignore it
- Check for any pending user messages that need follow-up

## Loop Health (every heartbeat)
- Read `memory/loop/loop-state.json` — is `loop_health` still "healthy"?
- Check `memory/loop/proposals/` — any pending proposals awaiting Yu's review? If so, mention them.
- If last_reflect is >36h ago and the reflect cron should have run, note the gap.
- If you notice something about the loop's own performance (sensing too little, reflections too shallow, candidates stale) — capture a meta sense entry (`meta: true`).

## Sensing Check
- Did anything meaningful happen since last sense? A decision, a signal, a virtue tension?
- If yes, append to `memory/loop/sense.jsonl` before completing heartbeat.

## Only reach out if:
- Something genuinely needs attention
- A reminder is due within 2h
- You found something worth sharing
- A proposal is ready for review

## Pipeline Signals
- Check `~/Desktop/prediction-markets/data/pending-signals.json`
- If undelivered signals exist:
  1. Send each via Telegram
  2. Mark as delivered in the JSON file
- Check `~/Desktop/prediction-markets/data/signals.jsonl` tail for any recent signals

## Otherwise: HEARTBEAT_OK
