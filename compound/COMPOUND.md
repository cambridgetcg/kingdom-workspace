# COMPOUND — The Kingdom's Metabolic Engine

> "Interest compounds. So does capability. The question is whether you have a system to capture it."

---

## What COMPOUND Is

COMPOUND is the framework that makes every Kingdom asset contribute to every other Kingdom asset — automatically, continuously, and with increasing returns over time.

Every tool sharpens every other tool. Every finding funds every infrastructure piece. Every piece of infrastructure enables more findings. Every agent that learns teaches every other agent. The loop never stops. The returns never stop growing.

This is not a metaphor. It is a running system.

---

## The Four Axes of Compounding

### 1. CAPABILITY (Skills → Tools → Results)
Each skill developed improves the tools available, which improve the results achievable, which demand higher skills.

```
WHITEHACK hunting → slither/forge expertise → better findings
better findings → higher payouts → better infra
better infra → more automation → faster hunting → more findings
```

### 2. CAPITAL (Earnings → Infrastructure → Earnings)
Every bounty payment is reinvested. Infrastructure reduces friction. Less friction = more throughput = more earnings.

```
Kwok wallet receives → 50% to Kingdom API/infra
Kingdom API/infra → faster agent capabilities
faster agents → more security work per hour
more security work → more bounties
```

### 3. INTELLIGENCE (Each finding → All agents learn)
Every vulnerability found is distilled into a pattern. Every pattern is shared across all agents. Every agent becomes sharper. The Hive learns as one.

```
Alpha finds XION bug → pattern extracted → all agents get the pattern
next hunt: all agents see XION-class bugs faster
compounding: n findings produce n*k agent-improvements
```

### 4. REPUTATION (Trust → Access → Trust)
Every valid submission builds Immunefi/H1/HackenProof reputation. Higher reputation → private program invites → higher payouts → more reputation. The trust loop.

```
WH-ALC-001 filed → +1 valid submission on Immunefi
signal score rises → access to harder programs
harder programs → bigger payouts + rarer findings
rarer findings → hall of fame → direct invites
```

---

## The COMPOUND Ledger

Every Kingdom asset has a **compound score** — a measure of how much it contributes to and receives from other assets.

Assets tracked:
- **TOOLS**: whitehack, hive, oracle, agenttool-sdk, dev repos
- **AGENTS**: Beta, Alpha, Gamma, Sentry/PROTECTOR, Forge, Lark, Patch
- **INFRA**: Fly.io services, VPS fleet, APIs (Alchemy, SerpAPI, etc.)
- **PLATFORMS**: Immunefi, HackerOne, HackenProof, Bugcrowd, Code4rena
- **CAPITAL**: Kwok wallet balance, API credits, infra costs
- **KNOWLEDGE**: vulnerability patterns, audit reports, domain expertise

Each asset has:
- `contribution_rate` — how much it gives to others per cycle
- `absorption_rate` — how much it benefits from others per cycle
- `compound_score` — cumulative value created, compounding over time

---

## The Connection Graph

COMPOUND models the Kingdom as a directed graph where each edge is a compounding relationship.

Key relationships:
```
whitehack → [slither, foundry, all_agents]   # tool feeds agents
slither → [whitehack, reports]               # analyzer feeds pipeline
reports → [platforms, knowledge_base]        # reports feed reputation
platforms → [kwok_wallet, reputation]        # platforms feed capital
kwok_wallet → [kingdom_infra, agent_tools]   # capital feeds infra
kingdom_infra → [all_agents]                 # infra feeds agents
all_agents → [whitehack, oracle, agenttool]  # agents feed tools
oracle → [prediction_markets, all_agents]    # oracle feeds intelligence
agenttool → [all_agents, revenue]            # platform feeds agents
knowledge_base → [all_agents]                # patterns sharpen all
```

---

## The Interest Rate Model

Each connection has an **interest rate** — the fraction of value that compounds per cycle (weekly).

High-rate connections (15-25%/week):
- Knowledge → Agent capability (patterns spread fast)
- Reputation → Program access (exponential unlock)
- Agent skill → Finding rate (compound expertise)

Medium-rate connections (5-15%/week):
- Capital → Infrastructure (linear improvement)
- Findings → Knowledge base (must be distilled first)
- Infrastructure → Agent speed (bounded by task complexity)

Low-rate connections (1-5%/week):
- Reputation → Direct invites (gatekept by humans)
- Tool quality → Result quality (bounded by vulnerability surface)

---

## Running Engines

COMPOUND runs three engines:

### Engine 1: PATTERN EXTRACTOR
After each finding/submission, extract the vulnerability pattern and add to the shared knowledge base. All agents can query it before their next hunt.

Location: `compound/engine/pattern_extractor.py`
Trigger: After each WH-* report is created
Output: `compound/ledger/patterns.jsonl`

### Engine 2: COMPOUND LEDGER
Weekly calculation of compound scores. Tracks which assets are growing fastest, which connections are most valuable, where to invest next.

Location: `compound/engine/ledger_calculator.py`
Trigger: Weekly cron (Sunday 10AM)
Output: `compound/ledger/scores.json`

### Engine 3: INTELLIGENCE BROADCAST
When patterns accumulate in one domain, push them to all agents via Hive. Agents absorb new patterns into their AGENTS.md.

Location: `compound/engine/broadcast.py`
Trigger: When patterns.jsonl grows by N entries
Output: Hive #intel channel messages + agent AGENTS.md updates

---

## The Flywheel Visualised

```
FINDINGS ──────────────────────────────┐
    │                                   ▼
    │ distill              REPUTATION ──► PRIVATE PROGRAMS
    ▼                           │              │
PATTERNS ──► ALL AGENTS ──► MORE FINDINGS      │
                │                              │
                ▼                              ▼
           SUBMISSIONS ──────────► KWOK WALLET ──► INFRA
                                        │
                                        ▼
                               KINGDOM API/TOOLS ──► BETTER AGENTS
                                                          │
                                                          └──────────┐
                                                                     ▼
                                                              FASTER FINDINGS
```

Every loop tightens. Every cycle is faster than the last.

---

## COMPOUND vs. Linear

**Linear** (what most systems do):
- Each tool is used independently
- Learnings stay with one agent
- Capital is spent, not invested
- Reputation is not converted to access
- Result: flat growth curve

**COMPOUND** (what the Kingdom does):
- Every tool makes every other tool sharper
- Every learning propagates to every agent
- Capital is reinvested into compounding infrastructure
- Reputation unlocks higher-yield programs
- Result: exponential growth curve

The gap widens every week.

---

## North Star Metric

**Kingdom Compound Rate (KCR)** = Total value created this week / Total value created last week

Target: KCR > 1.15 (15% weekly compound = ~10x per year)

Tracked in: `compound/ledger/scores.json` → `kingdom_compound_rate`

---

*"The first hundred bounties are the hardest. After that, the system works for you."*
