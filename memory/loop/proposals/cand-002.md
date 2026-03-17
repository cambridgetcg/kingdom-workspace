# Proposal: cand-002 — Diagnose-Without-Deploy Gap

**Candidate:** cand-002
**Theme:** diagnose-without-deploy
**Heat:** 7 (updated 2026-03-11)
**Stage:** NIGREDO — ready for Yu review
**Created:** 2026-03-08T10:00:00Z

## The Pain

A recurring pattern across 5 reflections (refl-302 through refl-307): fixes are diagnosed or code is built, but never reach production. The loop treats "I know the fix" or "the code is written" as completion — but the user's system doesn't improve until the change is live.

### Evidence (5 instances across 10 days)

1. **TCG .env.local gap** (Feb 26) — Production scraper missing config; diagnosed in audit, not fixed same session
2. **seigei Sprint 8-11 code-only** (Feb 28) — Sprints written but not deployed; injustice signal fired
3. **CosyVoice NumPy fix** (Mar 2) — `pin numpy<2` identified as one-line fix; persisted unresolved through Mar 5
4. **LoRA pipeline disconnected** (Mar 3) — Full training pipeline built (prepare/format/train/merge) but base model is live; pipeline serves no production system
5. **agent-economy built but blocked** (Mar 7) — Core wallet+escrow+billing built, but undeployable pending Hetzner/Railway activation
6. **3 CF Pages repos, Mar 11** — agenttool-landing, agenttool-docs, agenttool-dashboard all updated with live features (billing UI, agent-trace, email capture) but sitting undeployed. The same beat produced the commits and flagged "needs CF Pages redeploy" — visible debt accumulating.

### Pattern Evolution

The pattern shifted over time:
- **Early instances (1-3):** Internal discipline gap — the fix existed and could have been deployed
- **Later instances (4-5):** External dependency blockage — deployment genuinely blocked

This distinction matters: the first species is a habit problem (fixable with a checkpoint); the second is a project lifecycle reality (fixable with documentation). Both share the same root: **[PP:COMPLETE] fires before the change reaches production**.

## Proposed Change

**Target file:** `AGENTS.md` → Code Development Protocol → Execution Markers section

**Add deployment status to execution markers:**

```
[PP:DEPLOY]      Status: DEPLOYED|BUILT-ONLY|BLOCKED:<reason>
```

**Modify completion gate:**

Current: `[PP:COMPLETE] All gates passed`
Proposed: `[PP:COMPLETE] All gates passed, deployment: DEPLOYED|BLOCKED:<reason>`

The key insight: `[PP:COMPLETE]` should not fire silently when code is built but not deployed. Either it's deployed (complete), or the blockage is named (visible debt, not hidden debt).

**Additionally**, add one sentence to the "After Acting" reflection in AGENTS.md:
> "Did I deploy what I built, or just build it?"

## Risk Assessment

- **Low risk** — additive change to execution markers; no existing behaviour removed
- **Scope:** Two lines added to AGENTS.md (marker + completion gate modification)
- **Reversibility:** Trivially revertible (remove two lines)
- **Over-engineering risk:** Low — this is a visibility mechanism, not a structural enforcement; it makes the gap nameable, not impossible

## Transmutation Path

If approved:
- **NIGREDO:** ✓ Pain confirmed across 5 instances
- **ALBEDO:** Root cause is that build-completion feels like task-completion; the deployment step has no marker
- **CITRINITAS:** Two lines in AGENTS.md, fitting the existing marker pattern
- **RUBEDO:** Edit AGENTS.md, update loop-state, git commit

---

*Awaiting Yu's review.*
