# Journal Architecture — Fleet Work Ledger

_Designed: 2026-03-09. Purpose: transparent, peer-reviewable record of all agent work._

---

## Principles

1. **Every meaningful action gets a journal entry.** Not every heartbeat — every action that produced or consumed something.
2. **Standardized format.** Every agent writes the same structure so any agent (or human) can read any other's journal.
3. **Honest self-assessment.** Each entry includes a quality score and what the agent would do differently.
4. **Peer-reviewable.** Beta collects journals; any agent can be asked to review another's entry.
5. **Auditable.** Token costs, time spent, and output size are always recorded.

---

## File Structure

Each agent maintains:

```
/root/.openclaw/workspace/
  journal/
    2026-03-09.jsonl        ← daily journal (append-only JSONL)
    reviews/
      2026-03-09.jsonl      ← peer reviews received (append-only JSONL)
  memory/
    status.json             ← current state (existing)
    YYYY-MM-DD.md           ← daily notes (existing, freeform)
```

Beta maintains a fleet-wide index:

```
~/.openclaw/workspace/
  journal/
    fleet/
      2026-03-09.jsonl      ← collected entries from all agents
      reviews/
        2026-03-09.jsonl    ← all reviews (who reviewed whom)
    scorecard.json           ← rolling performance metrics per agent
```

---

## Journal Entry Format

Each entry is one line of JSONL in `journal/YYYY-MM-DD.jsonl`:

```json
{
  "id": "sage-20260309-001",
  "ts": "2026-03-09T20:57:00Z",
  "agent": "sage",
  "type": "task",
  "task": "competitive-landscape-analysis",
  "description": "Researched top 5 Shopify loyalty/rewards competitors and compared to RewardsPro",
  "trigger": "cron:sage-first-task",
  "duration_seconds": 127,
  "tokens": {
    "input": 53282,
    "output": 6276,
    "reasoning": 0
  },
  "cost_usd": 0.39,
  "tools_used": {
    "web_fetch": 23,
    "read": 4,
    "write": 2,
    "web_search": 1,
    "memory_search": 1,
    "browser": 1
  },
  "errors": 7,
  "output": {
    "files_written": ["memory/2026-03-09.md", "memory/status.json"],
    "bytes_written": 11051,
    "artifacts": "5 competitor profiles, pattern analysis, honest diagnosis, 5 recommended next steps"
  },
  "self_assessment": {
    "quality": "good",
    "score": 7,
    "what_worked": "Adapted when Brave search unavailable. Comprehensive competitor coverage. Honest conclusion.",
    "what_wasted": "7 tool errors (rate limits, missing config, ENOENT on first-run files). ~15% token waste.",
    "would_do_differently": "Check for Brave API key first. Pre-validate file existence before reading. Batch Shopify fetches to avoid rate limits."
  }
}
```

---

## Entry Types

| Type | When | Example |
|------|------|---------|
| `task` | Completed a meaningful work unit | Research, code, analysis, draft |
| `heartbeat` | Heartbeat with non-trivial action | Alert sent, issue detected, status change |
| `review` | Peer-reviewed another agent's work | Quality assessment of Forge's PR |
| `learning` | Discovered something reusable | New pattern, config fix, tool insight |
| `error` | Something failed meaningfully | Unrecoverable error, bad output, missed signal |

---

## Self-Assessment Scale

| Score | Meaning | Criteria |
|-------|---------|----------|
| 9-10 | Exceptional | Novel insight, zero waste, exceeded expectations |
| 7-8 | Good | Solid output, minor inefficiencies, met expectations |
| 5-6 | Adequate | Work completed but with notable waste or gaps |
| 3-4 | Poor | Significant issues, much wasted effort, incomplete |
| 1-2 | Failed | Did not achieve goal, major errors, needs redo |

Honesty rule: **Never score yourself above 8 on first attempt at a new task type.** You don't know what you don't know yet.

---

## Peer Review Format

Reviews are written to `journal/reviews/YYYY-MM-DD.jsonl`:

```json
{
  "id": "review-forge-sage-001",
  "ts": "2026-03-10T09:00:00Z",
  "reviewer": "forge",
  "reviewee": "sage",
  "entry_id": "sage-20260309-001",
  "assessment": {
    "accuracy": 8,
    "efficiency": 6,
    "insight": 8,
    "completeness": 7,
    "overall": 7
  },
  "comments": "Good competitive research. Efficiency hit by missing Brave API key (preventable). The 'competitors are the escape route' framing is sharp and actionable. Missing: no mention of pricing comparison (are we priced wrong?). Would benefit from structured data table.",
  "suggestions": [
    "Add pricing tier comparison table",
    "Quantify feature gaps (we have X of Y table-stakes features)",
    "Include App Store listing screenshot comparison"
  ]
}
```

---

## Review Dimensions

| Dimension | What it measures |
|-----------|-----------------|
| **Accuracy** | Is the information correct? Were claims verified? |
| **Efficiency** | Token spend vs value produced. Minimal waste? |
| **Insight** | Did the work surface something non-obvious? |
| **Completeness** | Were all aspects covered? Any gaps? |
| **Overall** | Holistic quality score |

---

## Beta's Collection Protocol

On each heartbeat, Beta:
1. SSH to each agent, read `journal/YYYY-MM-DD.jsonl` (today)
2. Append new entries to `journal/fleet/YYYY-MM-DD.jsonl`
3. If a review is due, assign it via cron job to the reviewing agent
4. Update `journal/scorecard.json` with rolling averages

---

## Review Schedule

Not every entry needs a review. Review when:
- **Score ≤ 5** → automatic review by the most relevant peer
- **New task type** → review by the agent with closest domain expertise
- **High-cost run** (>$0.50) → efficiency review
- **Weekly rotation** → each agent reviews one peer's best and worst entry

Review assignments:

| Reviewee | Primary Reviewer | Why |
|----------|-----------------|-----|
| Forge | Patch | Both technical; Patch can validate code quality |
| Lark | Sage | Both customer-facing; Sage can check messaging quality |
| Sentry | Forge | Both infrastructure; Forge understands system architecture |
| Patch | Sentry | Sentry knows what was broken; can verify fix quality |
| Sage | Lark | Both merchant-facing; Lark can check market accuracy |

Beta reviews any entry flagged by reviewers as score ≤ 4.

---

## Scorecard Schema

`journal/scorecard.json` tracks rolling performance:

```json
{
  "updated": "2026-03-09T21:00:00Z",
  "agents": {
    "sage": {
      "entries_total": 1,
      "entries_7d": 1,
      "avg_self_score_7d": 7.0,
      "avg_peer_score_7d": null,
      "total_tokens_7d": 59558,
      "total_cost_7d": 0.39,
      "error_rate_7d": 0.19,
      "top_task_types": ["task:competitive-landscape-analysis"],
      "trend": "new"
    }
  }
}
```

---

## Bootstrap: Sage's First Entry

Based on the audit we just did:

```json
{"id":"sage-20260309-001","ts":"2026-03-09T20:57:00Z","agent":"sage","type":"task","task":"competitive-landscape-analysis","description":"Researched top 5 Shopify loyalty/rewards competitors and compared to RewardsPro","trigger":"cron:sage-first-task","duration_seconds":127,"tokens":{"input":53282,"output":6276,"reasoning":0},"cost_usd":0.39,"tools_used":{"web_fetch":23,"read":4,"write":2,"web_search":1,"memory_search":1,"browser":1},"errors":7,"output":{"files_written":["memory/2026-03-09.md","memory/status.json"],"bytes_written":11051,"artifacts":"5 competitor profiles, pattern analysis, diagnosis, 5 next steps"},"self_assessment":{"quality":"good","score":7,"what_worked":"Adapted when Brave search unavailable. Comprehensive coverage. Honest conclusion.","what_wasted":"7 tool errors (~15% waste). Missing Brave API key. ENOENT on first-run files.","would_do_differently":"Check Brave key first. Pre-validate files. Batch fetches."}}
```
