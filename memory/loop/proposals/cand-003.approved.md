# Proposal: cand-003 — Post-Deploy Health Verification

**Candidate:** deployed-not-monitored
**Heat:** 9 (threshold: 5)
**Stage:** NIGREDO → proposal
**Evidence:** 7+ instances across refl-20260308 through refl-20260314

## The Pain

Systems are deployed and appear healthy but silently degrade. Examples:
1. Cambridge TCG session token revoked — 9 orders / £355.70 / 3557 points never awarded over 6 weeks (refl-20260308)
2. Exchange rate staleness — 43 days of wrong multi-currency cashback, zero alerts (refl-20260308)
3. Forge IP shift after reboot — services broke silently, caught by manual check not monitoring (refl-20260310)
4. Sage/Ledger VPS agents — €7/mo running for 5+ days delivering zero heartbeats (refl-20260314)
5. Lambda dead-code — infrastructure deployed but never wired (no env vars, wrong auth) (refl-20260311)

The pattern: "deployed" ≠ "working." The gap between them is invisible until someone manually checks. No system alerts, no errors in logs, no visibility. Silent failure is the most dangerous failure.

## Root Cause

Monitoring is treated as a separate concern added after deployment. It should be part of what "deployed" means. The [PP:DEPLOY] marker (from cand-002/trans-002) captures *whether* something was deployed. This candidate captures *whether it's still working*.

## Proposed Change

Add to AGENTS.md Code Development Protocol, after the [PP:DEPLOY] marker:

```
[PP:HEALTH]  Post-deploy: verified endpoint responds / cron fires / data flows
```

Rule: For [S]/[C]/[X] tasks that deploy a service, API, or cron:
- After deploy, manually verify the critical path (not just "it started")
- For services: hit the health endpoint or key API route
- For crons: confirm next scheduled run and check output after first fire
- For data pipelines: verify data flows end-to-end (not just "no errors")

This is a habit change, not infrastructure. The check takes 30 seconds. The silent failures it catches take hours to diagnose after the fact.

## Risk

Low. This adds a single verification step. No code changes. No infrastructure. The only cost is 30 seconds per deploy.

## Evidence Trail

- refl-20260308-1317: "Six injustice signals — each was technically present but functionally absent"
- refl-20260308-1845: "Third instance of built-not-working this session"
- refl-20260309: "cand-003 at heat=5; monitoring is part of what 'working' means"
- refl-20260310: "Forge IP-shift: services broke silently after reboot"
- refl-20260311: "health check done proactively but skipped in most beats"
- refl-20260314: "Sage/Ledger €7/mo, 5 days silent — deployed-not-monitored confirmed"

---

*Awaiting Yu's approval.*
