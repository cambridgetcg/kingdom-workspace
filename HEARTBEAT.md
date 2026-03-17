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
5. `rewardspro` — 8 active merchants, bug fixes + Sage/Canon findings only
6. `cambridge-tcg` — fix 8 failing tests, utcnow deprecation
7. `tcg-wholesale` — monitor only (active WIP, don't touch)

### Per-Beat Execution
1. Read `memory/dev-state.json`
2. Identify `activeRepo` and `activePhase`
3. Execute one unit of work
4. If phase complete → advance phase, update dev-state.json
5. If repo complete → move to next in queue, update dev-state.json
6. Commit with a clear message
7. Append to `memory/YYYY-MM-DD.md`
8. If something significant → message Yu

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

If a genuine opportunity is spotted → reach out immediately.

**New repo trigger**:
- [T/S] scope → create it, build it, report to Yu
- [C/X] scope → pitch to Yu first

---

## Otherwise: HEARTBEAT_OK
