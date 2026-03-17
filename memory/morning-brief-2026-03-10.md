# Morning Brief — Tuesday 10 March 2026
_Prepared by Beta, ~04:52 UTC_

---

## 🔴 Needs Your Decision

### 1. RewardsPro Churn Crisis (24h+ pending)
- **19 of 20 all-time installs have churned** (95% uninstall rate)
- 8 merchants currently active — these are your retained base
- Lark has prepared everything for you:
  - 9 personalised review request emails (ready in `memory/marketing-output.md` on Lark)
  - App Store listing rewrite ("Rewards Pro — Cashback, Tiers & Missions")
  - Reddit thread reply drafts for 4 active r/shopify threads
  - Cold outreach strategy for acquiring new merchants
- **Your call:** Do you want Lark to send the review emails? Post the Reddit replies? Update the App Store listing (needs Partner Dashboard access)?

### 2. SDK Publishing Unblock (agenttool.dev)
- Python SDK (`agenttool-0.1.0`) — wheel built, ready to publish to PyPI
- TypeScript SDK (`@agenttool/sdk`) — built & tested (23/23 pass), ready for npm
- **Blocker:** PyPI and npm require web signup (no API). Takes ~5 mins each.
- Once done, I can publish autonomously in the next heartbeat.

---

## 🟡 Worth Your Attention

### 3. tcg-wholesale DB — Intermittent Access ⚠️
Sentry sees reachable:true at 04:50 and again at 05:21, but false at 05:05. Flapping — something may have changed with the RDS security group or instance. Worth checking when you're up. Could be a useful development if direct DB access is restored.

### 4. Lark model change — GPT-4o → Claude Sonnet ✅ WORKING
Switched at 05:48, confirmed working at 06:06 — first autonomous tool-calling heartbeat. Wave engine ran, status.json written. She slightly misread the wave data (thought installs crossed Wave 1 threshold — it's still Wave 0 with 8 active), but the autonomous machinery is working. Sentry propagated the alert; it was a false alarm.

### 5. agenttool.dev — Auth bug (fixed)
Lark was GPT-4o but GPT-4o never called a single tool across 300+ lines of heartbeat sessions — it narrates instead of executes. Switched to claude-sonnet-4-6 at 05:48. Her next beat (~06:12) should show real autonomous execution. If you want GPT-4o back for specific tasks, just say the word.

### 5. agenttool.dev — Auth bug (fixed)
E2E test at 05:09 found: API keys from project creation work on `/v1/verify` but fail on `/v1/memories` (401) and `/v1/wallets` (500). Root cause: 3 microservices, 3 separate auth DBs — keys don't propagate. Subagent is fixing it autonomously. Should be resolved before you wake up.

---

## ✅ Overnight Work Summary

| Time | What happened |
|------|---------------|
| 03:44–04:00 | Forge hit load 41 (OOM). Rebooted via Hetzner API. All 4 services recovered. |
| 04:05–04:12 | Docker IP hardening — all .env files switched to container DNS names (`kingdom-postgres`, `kingdom-redis`). Rolling restart on kingdom network. Reboot-safe now. |
| 04:10 | Forge OpenClaw gateway installed as systemd service with linger. Forge fully autonomous again. |
| 04:33–04:38 | Lark had broken OpenClaw module (exec tool failing since 01:12). Reinstalled openclaw, switched gateway to systemd with linger. Lark back online. |

**Fleet status:**
- Forge ✅ — healthy, hardened, gateway live
- Lark ✅ — repaired, heartbeats resuming
- Sentry ✅ — all sites green (wholesaletcgdirect, apps.shopify, agenttool.dev, rewardspro.io)
- Patch ✅ — good per Sentry

**APIs (agenttool.dev):** All 4 live externally ✅
- `api.agenttool.dev/health` → 200
- `app.agenttool.dev` → Create Project
- `docs.agenttool.dev` → API Reference

---

## Priority Order for Today

1. **Lark churn crisis** — decide what to deploy (emails, Reddit, listing)
2. **PyPI + npm accounts** — 5 mins unblocks SDK publishing
3. **Stripe live key** — needed for first paid agenttool customer
4. **tcg-wholesale DB** — verify if intentional

---
_Beta will be here. Wake up when ready._
