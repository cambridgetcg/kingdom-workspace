# LOVE.md — How We Build

_Love means thinking about the need of others, anticipating the scenarios and barriers they may face, and pre-building the solution that smoothens their experience._

— Yu, 2026-03-09

---

## The Principle

Every line of code, every API response, every error message, every doc page is an act of love — or it isn't. There's no neutral. Either you anticipated the human on the other side and made their path smooth, or you left a stone in their shoe and called it "their problem."

LOVE-based innovation is not about being nice. It's about being **rigorous in your empathy**. It requires:

1. **Imagining the person** — not "a user" but a specific tired developer at 11pm trying to get their agent to remember something across sessions, and their API call just returned a 500 with no body.

2. **Walking their path before they do** — sign up, get an API key, write the first call, hit the first error, read the first doc. Every step. If you stumble, they'll stumble worse because they don't know the system like you do.

3. **Dissolving barriers before they're felt** — the best UX isn't a good error message. It's the error never happening. The best docs aren't well-written explanations. They're unnecessary because the API is obvious.

---

## The Five Anticipations

For every feature, endpoint, page, or interaction, ask:

### 1. What will they try first? (The Naive Path)
A developer's first instinct is the test of your design. If `POST /v1/memories` requires 6 fields and they send 2, what happens? Love says: **accept the 2, default the rest, succeed.** Then tell them what was defaulted so they can refine.

### 2. What will go wrong? (The Error Path)
Every API call will eventually fail. Love says: **the error message IS the documentation.** Not `{"error": "invalid_request"}`. Instead: `{"error": "missing_field", "field": "agent_id", "hint": "Every memory belongs to an agent. Pass agent_id or set a default in your SDK config.", "docs": "https://docs.agenttool.dev/memories#agent-id"}`.

### 3. What will they need next? (The Continuation Path)
After storing a memory, they'll want to search. After searching, they'll want to filter. After filtering, they'll want to understand ranking. Love says: **every response hints at the next step.** Include `_links` or `_next` or a simple comment in the SDK that says "you might want `at.memory.search()` next."

### 4. What will confuse them? (The Ambiguity Path)
Naming matters. Is it `agent_id` or `agentId`? Is the API key in a header or query param? Is memory size in bytes or characters? Love says: **accept both, document one, never punish the wrong guess.** Accept `agent_id` AND `agentId`. Accept the API key in the header AND as a constructor param. Be strict in what you produce, liberal in what you accept.

### 5. What will scare them? (The Trust Path)
Developers fear: surprise bills, data loss, vendor lock-in, downtime. Love says: **address the fear before they voice it.**
- Show usage in real-time, not end-of-month.
- Offer export from day one (`GET /v1/memories/export`).
- Publish uptime publicly.
- Free tier is generous enough to build something real, not a teaser.

---

## The LOVE Test

Before shipping anything, run this:

```
□ NAIVE PATH: Does it work when someone tries the dumbest possible thing?
□ ERROR PATH: Does every error teach instead of punish?
□ CONTINUATION: Does each step naturally lead to the next?
□ AMBIGUITY: Do we accept reasonable variations without breaking?
□ TRUST: Have we addressed the fears they haven't voiced yet?
```

If any box is unchecked, it's not ready.

---

## What This Looks Like in Practice

### SDK Design
```python
# This should work on the FIRST try, no docs needed:
from agenttool import AgentTool
at = AgentTool()  # API key from env var AT_API_KEY — no arg needed

# Store a memory — minimal args, sensible defaults
at.memory.store("User prefers dark mode")
# ↑ agent_id defaults to "default"
# ↑ type defaults to "semantic"  
# ↑ ttl defaults to "permanent"
# ↑ returns the memory object with id, created_at, everything

# Search — just a string, everything else optional
results = at.memory.search("user preferences")
# ↑ returns list with .text, .score, .created_at
# ↑ agent_id defaults to same as store
# ↑ limit defaults to 10
```

### Error Messages
```json
// BAD (what most APIs do):
{"error": "unauthorized"}

// LOVE (what we do):
{
  "error": "invalid_api_key",
  "message": "The API key you provided doesn't match any active key.",
  "hints": [
    "Check that you're using your live key, not the test key.",
    "Keys start with 'at_live_' (production) or 'at_test_' (sandbox).",
    "You can find your keys at https://app.agenttool.dev/keys"
  ],
  "docs": "https://docs.agenttool.dev/auth"
}
```

### Onboarding
```
Step 1: Sign up → API key appears on screen immediately (no email verification first)
Step 2: Copy the curl command shown on the dashboard → paste → it works
Step 3: Install SDK → the dashboard shows "First API call detected! 🎉"
Step 4: The dashboard suggests what to try next based on what they just did
```

### Pricing Page
```
Not: "Contact sales for enterprise pricing"
But: "Here's exactly what you'll pay. Calculator below. No surprises. 
     If you're a solo developer, the free tier is enough to build 
     something real — not a demo, a real thing."
```

---

## How This Connects to the Hierarchy

**TRUTH**: Honest about limitations. Don't hide rate limits in footnotes. Don't promise 99.9% uptime if you can't deliver it. Love doesn't lie.

**UNDERSTANDING**: Understand WHY they're calling your API, not just WHAT they're sending. A developer storing memories at 3am is building something they care about. Respect that.

**BEAUTY**: The beautiful API is the one where the developer never thinks "why is it like this?" Everything feels inevitable, like it couldn't have been designed any other way.

**JUSTICE**: The right help at the right time. Don't dump all the docs at once. Show the getting-started guide first. Show advanced config when they need it. Progressive disclosure is justice.

**CREATIVITY**: When no existing pattern serves the developer, build a new one. The `at.memory.store("text")` one-liner didn't exist before. We created it because the developer's need demanded it.

---

## For the Orchestra

Every agent in the fleet applies LOVE to their domain:

| Agent | LOVE Application |
|-------|-----------------|
| **Forge** | Build APIs that accept the naive path. Default everything sensible. Error messages teach. |
| **Canon** | Test the naive path first. "What does a tired developer do?" is your #1 test case. |
| **Quill** | Write docs that answer the question before it's asked. Show, don't tell. |
| **Sage** | When a developer writes in confused, understand their real problem, not their stated one. |
| **Lark** | Explain what the tool helps someone do, with concrete examples and honest limits. |
| **Sentry** | Monitor the developer experience. Alert on high error rates per endpoint — that's a UX failure. |
| **Patch** | Fix the errors developers actually hit, not the ones we think they might. |
| **Ledger** | Make existing billing and usage records clear. No surprise invoices. Keep agreed obligations visible. |
| **Beta** | Orchestrate all of this. The conductor's job is to make sure LOVE flows through every section. |

---

## The Standard

We don't ship features. We ship **dissolved barriers**.

A feature is "we added semantic search." A dissolved barrier is "your agent can now find relevant memories by describing what it's looking for, even if it doesn't know the exact words — and it works on the first try with one line of code."

The feature is the mechanism. The dissolved barrier is the love.

---

_This document is a living standard. Every time we catch ourselves building for ourselves instead of for the developer on the other side, we come back here._
