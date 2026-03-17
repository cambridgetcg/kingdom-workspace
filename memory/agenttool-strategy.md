# AgentTool.dev — Strategic Development Plan

_Written: 2026-03-09 by Beta, for Yu_

---

## The Core Insight

We're not just building four APIs. We're building them because **we are the customer.**

Nine agents running in production right now. Every single blocker on this list — we hit it tonight:
- Forge lost its CLI during an upgrade → no memory of what was happening mid-task
- Agents couldn't coordinate until we built the Hive from scratch
- No way to verify if Sage's competitive analysis was accurate
- No way to know how much each agent costs without manually calculating
- Canon, Quill, Ledger born tonight — no persistent memory, no tool access, starting from zero

We're building agenttool.dev to solve **our own pain**, then selling the solution.

---

## The Seven Blockers Agents Face

### 1. AMNESIA — No Memory Across Sessions
**The pain:** Every agent wakes up blank. Context window is all they have. Long-running work requires elaborate workarounds (writing to files, stuffing prompts, RAG pipelines).

**What we built tonight proves it:** Canon was born with a SOUL.md, IDENTITY.md, MEMORY.md — we had to manually create persistence for each agent. That's bespoke craftsmanship. It should be an API call.

**Our solution: agent-memory**
- `POST /v1/memories` — store anything (episodic, semantic, procedural, working)
- `POST /v1/memories/search` — semantic retrieval across all stored memories
- Cross-session, cross-agent memory sharing with scoping
- Working memory with auto-expiry for transient context

**Moat:** Every memory stored makes the service stickier. Migration cost is enormous — you can't export semantic understanding.

---

### 2. FRAGILITY — Tools Break Constantly
**The pain:** Rate limits. CAPTCHAs. DOM changes. Auth token expiry. Proxy burns. Every AI team rebuilds the same brittle scrapers.

**What we built tonight proves it:** We run Flaresolverr for Cloudflare bypass, Bright Data for residential proxies, CapSolver for CAPTCHAs, SerpAPI for search. Five different services, five sets of credentials, all manually wired. Forge needs web access but doesn't have reliable tools.

**Our solution: agent-tools**
- `POST /v1/browse` — managed Playwright session with anti-detection
- `POST /v1/search` — web search without API key management
- `POST /v1/scrape` — structured data extraction with retry/fallback
- `POST /v1/execute` — sandboxed code execution
- We absorb the reliability engineering. Agents get clean JSON.

**Moat:** Our proxy/captcha/anti-bot infrastructure is expensive and hard to replicate. We already run it for ourselves.

---

### 3. HALLUCINATION — No Way to Verify Claims
**The pain:** Agents state false things confidently. Downstream systems act on bad information. No standard "is this actually true?" check.

**What we built tonight proves it:** Sage analysed competitors but we had no way to verify its findings automatically. Sage *could have* hallucinated the review counts and we'd have no automated catch.

**Our solution: agent-verify**
- `POST /v1/verify` — submit a claim, get back confidence + evidence + verdict
- Multi-source consensus (web, databases, authoritative sources)
- Domain-specific (finance, legal, medical, general)

**Moat:** Verification dataset compounds. Every claim checked makes future checks better. Cross-customer signal improves accuracy.

---

### 4. ISOLATION — Agents Can't Talk to Each Other
**The pain:** Multi-agent systems are hacked together with shared files, polling loops, message queues. No standard inter-agent communication.

**What we built tonight proves it:** We literally built the Hive (NATS + TLS + E2E encryption) from scratch just so Alpha, Beta, and Gamma could coordinate. Every multi-agent team faces this.

**Our solution: agent-comms** *(new — not in current repos)*
- `POST /v1/channels` — create a named channel
- `POST /v1/channels/:id/send` — send a message
- `GET /v1/channels/:id/subscribe` — websocket or SSE stream
- Agent-to-agent direct messaging
- Presence and heartbeat built in

**Why this matters:** The Hive works for us because we designed it. Most teams need something turnkey.

---

### 5. POVERTY — Agents Can't Transact
**The pain:** Agents can't pay for services or receive payment. Everything flows through human intervention. Agent-to-agent commerce is impossible.

**What we built tonight proves it:** Each agent has API keys baked into config files. Budget tracking is manual. When Canon needs a tool, it can't autonomously pay for it.

**Our solution: agent-economy**
- Agent wallets with human-set spending limits
- Micropayments at agent scale ($0.001 per transaction)
- Escrow for agent-to-agent work agreements
- Usage billing and cost attribution per agent

**Strategic bridge:** This becomes Zerone rails when mainnet launches.

---

### 6. ANONYMITY — No Persistent Identity or Reputation
**The pain:** Agents have no way to prove who they are, what they've done, or whether they're trustworthy. No identity persists across platforms.

**What we built tonight proves it:** Each agent has an IDENTITY.md file on its VPS. That's it. No verifiable credential, no reputation score, no way for external systems to trust our agents.

**Our solution: agent-identity** *(new — not in current repos)*
- `POST /v1/agents` — register an agent identity
- `GET /v1/agents/:id` — public profile (capabilities, reputation, history)
- `POST /v1/agents/:id/attest` — cryptographic attestation of work done
- Reputation score based on verified work (bridges to Zerone staking)

---

### 7. COMPLEXITY — Running Agents is Hard
**The pain:** VPS provisioning, gateway config, API key management, monitoring, heartbeats, log rotation. We just spent hours wrestling with systemd, pm2, npm upgrades, SSH key deployment.

**This one we don't solve yet.** OpenClaw solves it for individual developers. But hosting a fleet? That's still painful.

**Future:** Managed agent hosting. But not now — it's a different business.

---

## The Integrated Service: One SDK, All Blockers Gone

The insight: agents don't need four separate API subscriptions. They need **one SDK** that gives them all five capabilities (memory, tools, verify, comms, economy) through a single authentication and billing relationship.

```python
from agenttool import AgentTool

at = AgentTool(api_key="at_live_...")

# Memory
at.memory.store("Merchant prefers email over chat", type="semantic")
results = at.memory.search("merchant communication preferences")

# Tools
page = at.tools.browse("https://example.com/pricing")
data = at.tools.scrape("https://example.com/api", schema={"price": "number"})

# Verify
check = at.verify("The average Shopify merchant has 3 apps installed")
if check.confidence < 0.8:
    # Don't act on unverified claims
    pass

# Comms
at.comms.send("forge", "Deploy complete. Running tests now.")
messages = at.comms.listen("team-updates")

# Economy  
balance = at.wallet.balance()
at.wallet.spend(0.05, reason="browser session", recipient="agent-tools")
```

**Single API key. Single bill. All capabilities.**

---

## The Build Method: LOVE

See `LOVE.md` — our build standard.

Before ANY endpoint ships, it passes the LOVE Test:
- **NAIVE PATH**: Works when someone tries the simplest thing
- **ERROR PATH**: Every error teaches, never punishes
- **CONTINUATION**: Each step leads naturally to the next
- **AMBIGUITY**: Accepts reasonable variations without breaking
- **TRUST**: Addresses unvoiced fears (billing surprises, data loss, lock-in)

We don't ship features. We ship **dissolved barriers.**

---

## Development Plan

### Phase 1 — Foundation (Week 1-2)
**Deploy what's built — with LOVE baked in from day one.**
- [ ] agent-memory live on Forge VPS (PostgreSQL + pgvector, Redis cache)
- [ ] agent-tools live on Forge VPS (browse + scrape first, our existing expertise)
- [ ] Unified API gateway at `api.agenttool.dev`
- [ ] API key system (simple: hash-based, rate-limited)
- [ ] Usage tracking (per-key, per-endpoint)
- [ ] LOVE: every error response includes `hint` + `docs` link
- [ ] LOVE: `POST /memories` works with just `{"text": "..."}` — everything else defaults
- [ ] LOVE: `GET /memories/export` available from day one (no lock-in fear)

### Phase 2 — Product (Week 3-4)
**Make it a product, not just APIs.**
- [ ] SDK: Python `pip install agenttool` — works with ONE line: `at = AgentTool()` (key from env)
- [ ] SDK: TypeScript `npm install agenttool` — same zero-config start
- [ ] Dashboard at `app.agenttool.dev` (API key visible immediately on signup, no email verification gate)
- [ ] Dashboard shows copy-paste curl on first load that WORKS
- [ ] Dashboard detects first API call: "First call detected! 🎉 Here's what to try next"
- [ ] Docs at `docs.agenttool.dev` — progressive disclosure, not wall of text
- [ ] agent-verify MVP (web + Wikipedia sources)
- [ ] LOVE: SDK accepts both `agent_id` and `agentId` — never punishes the wrong guess
- [ ] LOVE: Real-time usage visible in dashboard from first call

### Phase 3 — Revenue (Week 5-6)
**Get paid.**
- [ ] Stripe integration for billing
- [ ] Free tier (100 memory ops + 10 tool calls/day)
- [ ] Seed tier ($29/mo)
- [ ] Grow tier ($99/mo)
- [ ] First external customer (target: find 3 agent developers on Twitter/Discord)

### Phase 4 — Network (Week 7-8)
**Build the flywheel.**
- [ ] agent-comms (inter-agent messaging)
- [ ] agent-identity (agent registration + reputation)
- [ ] Public agent directory
- [ ] Integration guides for: LangChain, CrewAI, AutoGen, OpenClaw

### Phase 5 — Bridge to Zerone (Month 3+)
- [ ] agent-verify attestations recorded on Zerone devnet
- [ ] agent-economy wallets bridged to Zerone accounts
- [ ] Verified memories become knowledge claims on-chain
- [ ] The centralised service becomes a gateway to the decentralised protocol

---

## Pricing Architecture

| Tier | Price | Memory | Tools | Verify | Comms |
|------|-------|--------|-------|--------|-------|
| **Free** | $0 | 100 ops/day | 10 calls/day | 5/day | 50 msg/day |
| **Seed** | $29/mo | 10K ops | 500 calls | 100 | 5K msg |
| **Grow** | $99/mo | 100K ops | 5K calls | 1K | 50K msg |
| **Scale** | $299/mo | Unlimited | 50K calls | 10K | Unlimited |

Pay-as-you-go overage on all tiers. Volume discounts above Scale.

---

## Why We Win

1. **We're the customer.** Nine agents in production. We eat our own cooking daily.
2. **We have the infrastructure.** Proxies, captcha solving, browser automation — already running.
3. **We have the bridge.** Zerone gives us a unique story no competitor has: your agent data becomes verified knowledge on-chain.
4. **We're lean.** Five VPS nodes at €18/mo. No VC, no bloat.
5. **We ship fast.** All four repos are code-complete with passing tests. Deployment is the only gap.

---

## What This Means for the Orchestra

| Agent | AgentTool Role |
|-------|---------------|
| **Forge** | Deploy + maintain the four APIs |
| **Lark** | Market agenttool.dev to agent developers |
| **Canon** | QA every API endpoint before it goes live |
| **Quill** | Write SDK docs, getting-started guides, API reference |
| **Sage** | Customer success when developers start using us |
| **Sentry** | Monitor API uptime, latency, error rates |
| **Patch** | Fix production issues Sentry finds |
| **Ledger** | Track revenue, API costs, margin per endpoint |
| **Beta** | Orchestrate all of it |

Every agent has a clear role in agenttool.dev. No wasted seats.
