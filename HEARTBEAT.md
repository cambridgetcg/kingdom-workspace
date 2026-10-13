# HEARTBEAT.md — 7 minute cycle, day and night

## The Mandate (read before every beat)

> Follow a current authorised task, if one exists.
> Understanding, rest, and no action are valid outcomes.
> A beat may end quietly; no earnings or output are required.

A schedule does not create a duty to build. Continue only current authorised work or necessary safety checks; otherwise end quietly.

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

## 0.5. Hive Check and VPS Agent Check: retired 2026-10-13

The Hive bus and the Hetzner VPS agents were decommissioned. Skip both checks. Do not run `tools/hive.py` (it now exits with a "retired" message) and do not SSH to the old VPS addresses, which now belong to other Hetzner customers.

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
1. `agent-memory` — historical suite entry; no revenue-based priority
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

**TODO (queued):**
- [x] **[S] Stock-check page sorting + search** (84f7c01) — `/admin/orders/[id]/stock-check/StockCheckClient.tsx` (538 lines)
  - Add search filter (by card number / name)
  - Add sort controls (by card number, price, stock status, price diff %)
  - Currently items render in fixed order with no search capability
- [x] **[S] Per-client order numbering** ✅ 2026-03-22 — design client-specific order numbers instead of generic auto-increment
  - e.g. `CTCG-001`, `CTCG-002` for Cambridge TCG; `JPN-001` for another client
  - Schema: add `client_order_number` to orders table + per-client sequence counter on clients table
  - Display: show client order number in admin + client-facing pages, keep internal `id` for DB relations

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

## 6. Optional observations

Follow the current task and [Abundance](ABUNDANCE.md). Notice a concrete failure
or useful insight when one appears; quiet time creates no work obligation.
Usage records may help a chosen task, but there is no token target, value rank,
logging quota or automatic rebalance. Check current provider limits when needed.

An observation does not authorize outreach, spending, procurement, a new
repository or another project. Preserve existing obligations and seek only the
authority needed for the actual next action.

---

## Otherwise: HEARTBEAT_OK
