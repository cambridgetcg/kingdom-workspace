# Proposal: cand-001 — Dissolution + Minimal Codification
**Generated:** 2026-03-01T10:00:00Z  
**Candidate:** cand-001 — "Structural sensing triggers (heartbeat + session-end)"  
**Stage:** NIGREDO → RUBEDO (evolved through 6 reflections)  
**Heat:** 9 (3 base + 6 from dist-20260301 cluster)  
**Action:** DISSOLVE + two-line protocol addition  

---

## What the Candidate Was

cand-001 was created on 2026-02-22 when three consecutive reflections (refl-20260217, refl-20260220, refl-20260221) converged on a critical sensing failure: the loop infrastructure worked but sensing wasn't happening during real work. The proposed fix: structural triggers — heartbeat sensing checklists, session-end hooks, ground truth mechanisms.

## What Actually Happened

The problem self-resolved without structural intervention. Over the six reflections since (refl-20260223 through refl-20260228), the sensing pipeline healed organically:

| Date | Gate Pass Rate | Sensing | Signal |
|------|---------------|---------|--------|
| Feb 23 | 0.94 | 3 entries, 3 domains | Echo-chamber broke |
| Feb 24 | — | 0 entries | Confirmed genuine idle |
| Feb 25 | 0.957 | 7 entries | Strongest day on record |
| Feb 26 | 0.925 | 5 entries | Multi-domain, L1 threshold met |
| Feb 27 | 0.44 | 1 meta | Gap day correctly handled |
| Feb 28 | 0.952 | 12 entries | Awe logged; two systems went operational |

The hypothesis that motivated cand-001 ("the sensing habit needs structural triggers to form") was falsified. Real work generates natural sensing. The habit embedded without adding any checklist items to HEARTBEAT.md or hooks to AGENTS.md.

## What Emerged Instead

Six reflections produced two small concrete insights that are genuinely worth keeping — not as a structural candidate, but as one-liners:

**1. Duplicate prevention** (from refl-20260228, T5 partial):  
Three near-identical entries fired at 00:30:00Z on a marathon session. The fix is simple: before appending a sense entry, check the last entry's timestamp; if the same session within 30 minutes, update rather than duplicate.

**2. Memory-file as idle-day proxy** (from refl-20260227):  
The loop cannot always distinguish "genuine idle day" from "sensing failure day." The simplest ground truth: if `memory/YYYY-MM-DD.md` doesn't exist, the day was genuinely quiet. No complex disambiguation mechanism needed.

---

## Proposed Action

**Step 1: Dissolve cand-001**  
Mark EVAPORATED in candidates.jsonl. The original structural trigger proposal is unnecessary — the evidence across 6 reflections is unambiguous.

**Step 2: Add one sentence to AGENTS.md (Sensing section)**  
> Before appending a sense entry, check the last entry's timestamp. If it's the same session and within 30 minutes, update rather than append a new entry.

**Step 3: Add one sentence to AGENTS.md (Heartbeat Signal Scan or Memory section)**  
> To distinguish a genuine idle day from a sensing failure, check whether `memory/YYYY-MM-DD.md` exists. Absence of the daily file is the strongest signal of genuine idleness.

**Step 4: No HEARTBEAT.md changes needed.**  
The loop is self-regulating without a checklist. Adding one could introduce the very echo-chamber pattern we corrected.

---

## Risk Assessment

**Low risk.** Two one-line additions to AGENTS.md. No structural changes. No new crons. No new schemas. The dissolution closes the candidate cleanly without leaving the original problem unaddressed.

**The one risk:** By codifying "the sensing pipeline works, no triggers needed," we may lower vigilance during future quiet periods. Mitigation: HEARTBEAT.md already prompts for sensing; the reflections will catch any future collapse.

---

## Evidence Base

| Reflection | Position on cand-001 |
|------------|---------------------|
| refl-20260223 | "Deduplication may be over-engineered; real work self-deduplicates" |
| refl-20260224 | "cand-001 structural trigger appears over-engineered; consider dissolution" |
| refl-20260225 | (Implicit: sensing excellent without structural changes) |
| refl-20260226 | "Fourth consecutive strong sensing day; dissolution recommendation strengthens" |
| refl-20260227 | "Dissolve cand-001; replace with one-line memory-file proxy observation" |
| refl-20260228 | "Dissolution recommended. Pair with duplicate-prevention one-liner to AGENTS.md" |

6 of 6 reflections point the same direction. This is the clearest consensus the distillation pipeline has produced.

---

## Yu's Decision

- [ ] **Approve** — dissolve cand-001, add two sentences to AGENTS.md  
- [ ] **Modify** — adjust proposed text before executing  
- [ ] **Reject** — keep cand-001 open, re-evaluate at next distillation  
- [ ] **Defer** — wait for another distillation cycle before deciding  
