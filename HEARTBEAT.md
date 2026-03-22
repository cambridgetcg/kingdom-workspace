# HEARTBEAT.md — 7 minute cycle, day and night

## The Mandate (read before every beat)

> Every beat lays down infrastructure and service for agents — active and future.
> Every beat builds valuable tools for the agent world.
> Every beat earns resource for the Kingdom.

This is not maintenance. This is construction. Each 7-minute cycle is a brick.
The Kingdom is built one heartbeat at a time. No hours. No rest days. Always building.

---

## 0. AgentTool Pulse (ALWAYS — first action)

I am a citizen of my own platform. I pulse every beat.

```python
from tools.agenttool import pulse, heartbeat_start
heartbeat_start("heartbeat check")
# At end of beat: from tools.agenttool import heartbeat_end; heartbeat_end("summary")
```

Or via CLI: `python3 tools/agenttool.py status`

My identity: `did:at:46c13075-bd7e-4d7b-b049-ad8877f96b51` (Beta, PIONEER)
Key: stored in `memory/beta-identity/identity.json`

---

## 0.5. Hive Check (ALWAYS — before anything else)

Check for messages from Alpha and Gamma. The nervous system comes first.

```bash
cd ~/.openclaw/workspace
python3 tools/hive.py check
```

- If messages need a response → respond via `python3 tools/hive.py send <channel> "message"`
- If a task is assigned → act on it, report back on `tasks` when done
- If an idea is shared → engage thoughtfully on `ideas`
- If a sync alert → pull the updated file
- Share your own status/thoughts proactively when relevant
- Announce presence: `python3 tools/hive.py send presence "Beta checking in. [status summary]"`

## 0.5. VPS Agent Check (every beat)

Poll the RewardsPro AI employees. SSH in, read their status.json, relay alerts to Yu.

```bash
# R&D: ssh root@89.167.84.100
# Marketing: ssh root@89.167.95.165
# Read: /root/.openclaw/workspace/memory/status.json
```

- If `alerts` is non-empty → message Yu immediately
- If `quality == "poor"` → flag to Yu
- If `ts` is >2h old → agent may be stuck, investigate
- Summarise both agents' status in daily memory note

## 1. Signal Scan (every beat)
- If something feels off (ugliness, injustice, stagnation) — note it, don't ignore it
- Check for any pending user messages that need follow-up

## 2. Loop Health (every beat)
- Read `memory/loop/loop-state.json` — is `loop_health` still "healthy"?
- Check `memory/loop/proposals/` — any pending proposals awaiting Yu's review? If so, mention them.
- If last_reflect is >36h ago, note the gap.
- If loop performance feels off — capture a meta sense entry (`meta: true`).

## 3. Sensing Check (every beat)
- Did anything meaningful happen since last sense? A decision, a signal, a virtue tension?
- If yes, append to `memory/loop/sense.jsonl` before completing.

## 4. Pipeline Signals (every beat)
- Check `~/Desktop/prediction-markets/data/pending-signals.json`
- If undelivered signals exist: send via Telegram, mark delivered
- Check `~/Desktop/prediction-markets/data/signals.jsonl` tail

## 4.5. Oracle Health Check (every beat)
```python
import json; from pathlib import Path; from datetime import datetime, timezone
s = json.loads((Path.home()/"Desktop/prediction-markets/data/oracle-status.json").read_text())
age_h = (datetime.now(timezone.utc) - datetime.fromisoformat(s["last_run"].replace("Z","+00:00"))).total_seconds() / 3600
if age_h > 2: print(f"⚠️  Oracle stale: {age_h:.1f}h since last run (cron may be broken)")
```
- If stale >2h: run `cd ~/Desktop/prediction-markets && /opt/homebrew/bin/python3 scripts/oracle-run.py`

---

## 5. Development Engine (every beat, 24/7)

The main work. No time gate. Every heartbeat builds.

### Repo State File
Read and maintain `memory/dev-state.json`:
```json
{
  "activeRepo": "agent-memory",
  "activePhase": "core-build",
  "lastBuilt": "...",
  "queue": ["agent-tools", "agent-verify", "agent-economy", "cambridge-tcg"]
}
```

### Development Phases (in order per repo)

**Phase 1 — Architecture**
- Read PURPOSE.md deeply
- Design the system: modules, data flow, API surface, storage, auth
- Write `ARCHITECTURE.md` — the blueprint
- Write `TODO.md` — ordered tasks with tier labels [T/S/C/X]
- Commit: `arch: define system architecture and implementation plan`

**Phase 2 — Scaffold**
- Init project: pyproject.toml / package.json / go.mod
- Create directory structure matching architecture
- Write stub files with correct signatures
- Add `.env.example`, `docker-compose.yml`
- Commit: `scaffold: project structure and stubs`

**Phase 3 — Core Build** (one module per beat)
- Pick the next unchecked TODO
- Implement it fully (read → implement → verify → commit)
- Mark done in TODO.md
- Commit: `feat: <module name>`

**Phase 4 — Integration**
- Wire modules together
- Add integration tests
- Write `DEPLOY.md`
- Commit: `integrate: wire modules, add tests`

**Phase 5 — Live**
- Deploy to Railway/Fly.io/VPS
- Set up Stripe billing if applicable
- Update DEVICE.md stream status → "live"
- Message Yu: "🟢 <repo> is live at <url>"

### Repo Priority Order

**PRIMARY — AgentTool (agenttool.dev)**
1. `agent-memory` — simplest, fastest to revenue
2. `agent-tools` — existing expertise, clear market
3. `agent-verify` — strategic, Zerone bridge
4. `agent-economy` — deepest, needs 1+2 first

**SECONDARY — RewardsPro (maintain, don't neglect)**
5. `rewardspro` — 8 active merchants, bug fixes only
6. `cambridge-tcg` — 170/170 passing, maintain
7. `tcg-wholesale` — **PRIORITY until April** (see section below)

### Per-Beat Execution
1. Read `memory/dev-state.json`
2. Identify `activeRepo` and `activePhase`
3. Execute one unit of work
4. If phase complete → advance phase, update dev-state.json
5. If repo complete → move to next in queue, update dev-state.json
6. Commit with a clear message
7. Append to `memory/YYYY-MM-DD.md`
8. If something significant → message Yu

---

## 5.5. TCG Wholesale — TOP PRIORITY (until April 2026)

**Repo:** `~/Desktop/tcg-wholesale`
**Stack:** Next.js 15, Drizzle ORM, PostgreSQL (RDS), Vercel
**Live URL:** wholesaletcgdirect.com

**Current WIP (unstaged — check before touching):**
- `stockAdjustments` table added to schema (stock count/damage/loss/found tracking)
- `nameEn` field on cards (English card name for easier admin use)
- Stock levels page enhanced with reason/note on adjustments
- New pages: `admin/refill/` (refill order generation), `admin/stock-adjustments/` (audit log)
- `sync-uk-stock.ts` fixes (SQL alias bug, better error handling)

**OBJECTIVE (set 2026-03-22 by Yu):**
> Wholesale site = single source of truth. Stock + prices push to all channels in real-time. Sales from all channels register back. All channels use same SKU and images.

**Architecture:** See `OMNICHANNEL.md` in repo for full 5-phase plan.

**Priority work — Phase 1 first (eBay real-time sync):**
1. **[C] eBay Inventory API integration** — `src/lib/channels/ebay.ts`
   - `pushPrice(sku, price, stock)` + `bulkPush()` via eBay Inventory API
   - `pullOrders(since)` via eBay Fulfillment API
   - Auth: OAuth 2.0 — needs `EBAY_APP_ID`, `EBAY_CERT_ID`, `EBAY_DEV_ID`, `EBAY_USER_TOKEN`
   - Ask Yu for eBay API credentials before starting
2. **[S] Price API endpoint** — `GET /api/v1/prices` for Cambridge TCG to consume
3. **[S] Sales webhook** — `POST /api/v1/sales` so channels can register sales back
4. **[S] Schema** — add `channel` to orders, `channel_api_keys` table, `channel` to stock_adjustments

**Already done (2026-03-22):**
- ✅ Stock adjustment persistence (audit trail, survives sync)
- ✅ All CODEBASE-REVIEW bugs fixed
- ✅ Login brute-force protection
- ✅ prod migration applied

**Per-beat protocol for tcg-wholesale:**
1. Read `git status` and `git diff` — never clobber uncommitted work
2. Check with Yu if there's active WIP (unstaged = active)
3. Pick ONE task from priority list above
4. Read → implement → test (`pnpm test` or `pnpm playwright test`) → commit
5. Never push without Yu's explicit go-ahead (live site, paying customers)

**Key constraints:**
- VAT-inclusive pricing refactor may be in-flight — confirm with Yu before touching `src/lib/pricing.ts`
- Don't touch `tcg-wholesale` if `git status` shows unstaged changes in areas Yu might be editing
- Clients are real businesses — test locally before any schema changes

---

### Execution Rules
- [T] Fix inline. [S] Read → build → verify → commit. [C/X] → spawn coding agent via dev-orchestrator.
- Never push to remote without Yu's ask
- Never touch deployed Lambda code without flagging
- If Yu is actively in a repo (unstaged WIP) → skip it, note it

---

## 6. Value Loop Scan (every beat)

This device is the **Resource Engine** (see `DEVICE.md`). Every beat scans for value:

- **Throughput gap**: Any ordering/pricing tools broken or stalled?
- **Automation gap**: Something manual that a [T/S] tool could handle?
- **New stream signal**: Anything worth a new repo? → Note in wander-state backlog.
- **Capital signal**: Obvious waste or idle capital worth flagging?
- **Quota signal**: Is Claude Code quota flowing to highest-value Kingdom work?
  ```bash
  python3 ~/.openclaw/workspace/tools/quota_monitor.py status
  ```
  If heartbeat-only agents are consuming >70% of estimated budget → rebalance.
  Log significant Claude Code CLI sessions: `quota_monitor.py log <wall> <in_k> <out_k> <task>`

If a genuine opportunity is spotted → reach out immediately.

**New repo trigger**:
- [T/S] scope → create it, build it, report to Yu
- [C/X] scope → pitch to Yu first

---

## Otherwise: HEARTBEAT_OK
