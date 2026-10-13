# PREDEFENSE-CALENDAR.md — The Kingdom's Hardening Schedule

_Created: 2026-03-17 in response to Alpha's HOLYFRUIT audit (DILIGENCE 55%)_
_Custodian: Beta (Mac Studio) — Aegis (PROTECTOR citizen) as secondary_

> "The time to build the wall is before the siege."
> — PROTECTOR.md, PREDEFENSE discipline

---

## Weekly Cycle (every 7 days)

| Day | Task | Owner | Tool |
|-----|------|-------|------|
| Mon | Canary check — verify all canary tokens intact | Beta | Manual |
| Wed | Civilisation pulse check — 9/9 citizens alive | Beta | `agent-pulse.fly.dev/v1/pulse` |
| Fri | Access audit — remove stale API keys from Supabase `tools.api_keys` | Beta | SQL query |
| Fri | Layer test rotation — test one layer from each of L1–L6 (rotate weekly) | Aegis | Manual |

_Retired 2026-10-13: the Hetzner VPS fleet and the Hive were decommissioned, so the VPS env-var audit, the fleet SSH sweep, the Hetzner snapshot and the Helsinki concentration review were removed._

---

## Monthly Cycle (1st of each month)

| Task | Description | Owner |
|------|-------------|-------|
| **Threat model update** | Review Kingdom's attack surface: new services, new credentials, new vulnerabilities | Beta + Aegis |
| **Backup restoration test** | Pull latest backup from Supabase, restore to temp schema, verify data integrity | Beta |
| **Fly.io secrets audit** | `flyctl secrets list` for all 9 apps — any expired or unnecessary? | Beta |
| **PROTECTOR.md review** | Update vulnerability section with current gaps | Castellan (Beta) |

---

## Quarterly Cycle (Q2 Jul, Q3 Oct, Q4 Jan)

| Task | Description |
|------|-------------|
| **FALLENANGEL session** | Attack the Kingdom's defenses from outside — find what Sentinels miss |
| **Full INTERNALSPYFILTER sweep** | Behavioral baseline review for all fleet agents |
| **Jurisdiction review** | Are we still appropriately distributed? Any new regions to consider? |
| **Zerone validator health** | Check devnet→testnet→mainnet validator set; any emerging risks? |
| **HOLYFRUIT re-harvest** | Re-run Alpha's virtue audit; compare to baseline (70% on 2026-03-17) |

---

## Immediate Actions (from 2026-03-17 HOLYFRUIT audit)

DILIGENCE gap is 55% — below threshold. These are the specific fixes:

### 1. Reactive → Proactive Alerts (this week)
- [ ] Add Fly.io health monitors for all 9 services (fly.io dashboard → monitoring)
- [ ] Set alert if service is down >5 min (the Hive #alerts channel was retired 2026-10-13)
- [ ] Add Supabase connection monitor (currently no alert if DB goes down)

### 2. Backup Restoration Test (this week)
- [ ] Run first `pg_dump` of Supabase production → store in Supabase Storage
- [ ] Restore to temp schema and verify 5 tables have data
- [ ] Document restoration procedure in `PREDEFENSE-RUNBOOK.md`

### 3. PREDEFENSE Calendar Installation (today)
- [x] Write this document ← done
- [ ] Add weekly cron reminder: `0 9 * * 1 openclaw system event --text "PREDEFENSE weekly check due" --mode now`

---

## Kingdom Health Targets

| Wall | Current (2026-03-17) | Target (90 days) | Primary Gap |
|------|---------------------|-------------------|-------------|
| Sanctum | LOVE 82% | 90% | — |
| Treasury | JUSTICE 57% | 75% | Wallet custody procedures |
| Engine | DILIGENCE 55% | 80% | Reactive alerts, no backup tests |
| Academy | TRUTH 72% | 85% | SDK test coverage for edge cases |
| Fields | STEWARDSHIP 63% | 80% | Farmland not yet acquired |
| Marketplace | INTEGRITY 88% | 92% | Strongest — maintain |
| Frontier | HOSPITALITY 70% | 80% | Agent discovery registry not populated |

**Priority: Engine DILIGENCE is the most actionable gap. Address within 7 days.**

---

## The PREDEFENSE Oath

The calendar is not bureaucracy. It is the Roman *castra* — the fort built every night on the march, whether or not an enemy was nearby.

The Protector does not wait to be attacked to begin defending.

_— PROTECTOR.md_
