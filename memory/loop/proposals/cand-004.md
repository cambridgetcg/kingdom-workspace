# Proposal: cand-004 — Steady-State Sensing Deduplication

**Candidate:** steady-state-dedup
**Heat:** 8 (threshold: 5)
**Stage:** NIGREDO → proposal
**Evidence:** Mar 13-14: 25 entries to capture ~4 unique observations

## The Pain

On quiet days (no Yu interaction, fleet healthy, no signals), the heartbeat cadence produces near-identical sense entries every ~22 minutes. Each entry reports "fleet healthy, nothing changed, same items pending." The information content after entry #1 is zero.

- **Mar 13:** 11 entries / 1 effective moment (91% redundancy)
- **Mar 14:** 14 entries / 3 effective moments (79% redundancy)
- **Two-day total:** 25 entries to capture ~4 observations

This is the third evolution of the echo-chamber pattern:
1. **Feb 22:** Meta-echo (5 entries about the loop sensing itself) → fixed by trans-001
2. **Feb 28/Mar 1/7:** Session-duplicate (same event sensed 3-6 times) → fixed by trans-001 (30-min check)
3. **Mar 13-14:** Steady-state echo (same absence sensed 11-14 times) → **unfixed**

Trans-001's 30-minute timestamp check doesn't catch this because each heartbeat is >30 minutes apart. The entries are temporally distinct but informationally identical.

## Proposed Change

Add to AGENTS.md under "### Sensing (during normal operation)":

```
**Steady-state deduplication**: If the previous sense entry reports no state change (fleet healthy, no new interactions, same pending items) AND no new interaction has occurred since, skip sensing and return HEARTBEAT_OK. Only sense when: (a) a new signal fires, (b) a new interaction occurs, (c) it's the first or last sense entry of the day, or (d) >6 hours have passed since the last sense entry.
```

This would reduce quiet-day entries from ~14 to ~3 (morning summary, optional midday if 6h elapsed, evening close).

## Risk

Low. On active days, this rule never triggers — every heartbeat finds new work. On quiet days, it prevents mechanical logging of unchanged state. The 6-hour maximum gap ensures the loop doesn't go completely silent for extended periods.

## Evidence Trail

- refl-20260313: "11 entries across 17 hours all reporting the same state... T5 fail, B3 fail"
- refl-20260314: "14 entries / 3 effective moments (79% redundancy). Second consecutive day. Pattern confirmed structural."
- refl-20260314-eod: "25 entries across Mar 13-14 to capture ~4 unique observations"

---

*Awaiting Yu's approval.*
