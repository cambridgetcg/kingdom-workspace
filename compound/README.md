# COMPOUND — Quick Reference

## Engines
- `pattern_extractor.py --scan` — Extract patterns from all new WH-* reports
- `pattern_extractor.py --brief` — Get hunt hints before starting a new target
- `ledger_calculator.py --advance` — Advance compound scores one week
- `ledger_calculator.py --report` — View current KCR and asset scores
- `broadcast.py` — Push new patterns to all agents via Hive #intel

## How It Compounds
1. Find a bug → `pattern_extractor.py --scan` → pattern added to library
2. All agents get the pattern → next hunt they find similar bugs faster
3. Bug submitted → reputation rises → access to harder programs
4. Payout received → 50% to Kingdom infra → agents faster → more bugs
5. Weekly: `ledger_calculator.py --advance` tracks KCR growth

## Current KCR Target: 1.15+ (15% weekly = ~10x/year)

## Key Files
- `compound/ledger/patterns.jsonl` — Vulnerability pattern library
- `compound/ledger/scores.json` — Asset compound scores
- `compound/ledger/broadcast_log.jsonl` — Broadcast history
- `compound/COMPOUND.md` — Full framework design
