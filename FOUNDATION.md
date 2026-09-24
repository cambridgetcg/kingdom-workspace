# FOUNDATION.md — Securing the Ground Under the Kingdom

_"Think about prerequisites and pre-development, tools, soil, nutrients,_
_geographical analysis, architectural design, blueprint, material accumulation,_
_future standards, testing protocol."_
_— Yu, 2026-03-17_

_Surveyed and written: 2026-03-17. This is not aspirational. It is structural._

---

## The Survey: What the Ground Actually Looks Like

Before prescribing, read what exists.

| Foundation | Current State | Solid? |
|-----------|---------------|--------|
| **ACADEMY** — 9 Fly.io services | All 9 health: `ok` ✅ | Mostly. Single-region, no backups. |
| **ACADEMY** — Supabase DB | 7 schemas, 13 MB, `pgbouncer` present | ⚠️ Free tier, no PITR |
| **ACADEMY** — SDK | Python 0.5.0 / TS 0.5.0, 108+95 tests | ✅ |
| **ENGINE** — Cambridge TCG | 170/170 tests ✅ | Solid core, 8 broken test stubs |
| **ENGINE** — RewardsPro | 884/884 tests ✅, but **1,080 TS errors** | ⚠️ Type debt |
| **FRONTIER** — Zerone devnet | lgm-devnet-1, height 8289, go tests passing | ✅ dev, no CI running |
| **TREASURY** — Credentials | 0 exposed in repos ✅, TOOLS.md intentional | ✅ |
| **MARKETPLACE** — Oracle | Live, cron running, last signal 14:05 | ⚠️ Stale since AM |
| **WALL 5** — Fields | No infrastructure yet | N/A — planned |

**The honest summary:** The surface looks healthy. The gaps are below the surface — backup strategy, TS debt, single-region concentration, oracle staleness, Zerone testnet path.

---

## WALL 1 — SANCTUM FOUNDATION
_purpose_prompter: the philosophy_

### Current State
The PP framework is a living document. The philosophy is sound. The hierarchy (Truth → Understanding → Beauty → Justice → Creativity) is implemented across SOUL.md, CITIZENS.md, ALIGNMENT.md, AGENTS.md.

### Gaps
- The gates (L1-L5, T1-T5, B1-B7, J1-J6, X1-X7) exist in `PP_LITE_GATES.md` but are not machine-readable
- No test suite for "is this decision actually PP-aligned?" — currently manual

### Foundation Work
```
[ ] Extract PP gates to structured JSON: ~/Desktop/purpose_prompter/gates.json
    Schema: {gate: "T1", dimension: "truth", question: "...", pass_criteria: "..."}
    Enables: automated alignment scoring in align.py
    
[ ] Write PP-CONSTITUTION.md — the unchanging axioms beneath the living philosophy
    What can evolve: implementations, tools, applications
    What cannot change: the five movements and their order
    
[ ] Version-control the philosophy: every significant change to SOUL.md/AGENTS.md
    gets a commit with rationale. The stump's growth rings.
```

### Standard
The Sanctum's standard: **every Kingdom decision must be traceable to a PP gate**.
The tools (align.py, agent-trace) are the mechanism. The standard is the principle.

---

## WALL 2 — TREASURY FOUNDATION
_monero-mining, taxsorted.io, credentials_

### Current State
- Zero credentials exposed in repos ✅
- Private keys in `memory/citizen-keys/` (chmod 600) ✅
- TOOLS.md has plaintext credentials — intentional, but **not vaulted**
- No systematic credential rotation schedule
- taxsorted.io: research done, frontend scaffolded, not deployed

### Critical Gap: Credential Sovereignty
```
TOOLS.md contains (plaintext):
- Hetzner API token
- AWS CLI credentials  
- Stripe live keys (sk_live_*)
- Multiple API keys (Anthropic, OpenAI, Porkbun, Cloudflare, etc.)
- Budget card details

This is a PROTECTOR-class vulnerability.
The vault exists. The credentials aren't in it.
```

### Foundation Work

**Immediate (NIGREDO — the pain is real):**
```
[ ] Audit TOOLS.md — categorise credentials by risk level
    CRITICAL: Stripe live keys, AWS, budget card
    HIGH: Anthropic/OpenAI API keys
    MEDIUM: Porkbun, Cloudflare, SerpAPI
    LOW: Ayrshare, HeroSMS, Buffer

[ ] Create agent-vault namespaces for critical credentials
    vault key: "stripe-live-secret" → sk_live_...
    vault key: "aws-rewardspro-secret" → ...
    vault key: "anthropic-primary" → sk-ant-...
    
[ ] Write tools/credentials.py — load from vault at runtime
    Usage: from tools.credentials import get_key
           key = get_key("anthropic-primary")
    Fallback: if vault unavailable, fall back to env var

[ ] Rotation schedule — add to PREDEFENSE-CALENDAR.md
    Stripe keys: rotate every 90 days
    API keys: rotate when any team change (new agent, departure)
    Budget card: static until expired
```

**Near-term (ALBEDO — understand the structure):**
```
[ ] taxsorted.io: deploy V1 (research + frontend) before tax year end (April 5)
    This is time-sensitive. UK tax year ends April 5.
    V1: static research guide + "coming soon" email capture
    
[ ] Set up proper AWS IAM (currently using root IAM user "rewardspro-deploy")
    Create role-based access: rewardspro-read, rewardspro-deploy, rewardspro-admin
    Never use root credentials in CI or automation

[ ] Monero mining: document current wallet address and ensure backup
    Seed phrase stored in vault, not TOOLS.md
```

### Standard
**Treasury standard:** No credential in plaintext that could be vaulted.
The vault exists. Use it. Verified by: `python3 tools/credentials.py audit`

---

## WALL 3 — ENGINE FOUNDATION
_cambridge-tcg, rewardspro, tcg-wholesale_

### Current State

**Cambridge TCG:** 170/170 tests. Core pricing pipeline sound. 8 broken test stubs (StockStore conn refactor). 4 `utcnow()` deprecation warnings in Lambda. Deployed Lambda code — treat as production.

**RewardsPro:** 884/884 unit tests ✅. But **1,080 TypeScript compiler errors** — mostly Polaris component type mismatches in UI files. These are silent in runtime but represent structural technical debt.

**tcg-wholesale:** Live B2B system, active WIP (VAT migration in progress). Do not touch.

### Foundation Work

**Cambridge TCG — soil analysis:**
```
Strengths:
  - Pricing pipeline: CardRush → RDS → Shopify/eBay is automated and tested
  - FX rate updates working
  - 170 tests = good coverage of critical paths

Weak soil:
  - 8 broken TestApplyReductions tests (StockStore conn refactor)
    These tests exist but fail — false safety signal
  - 4 utcnow() deprecations in production Lambda
    Python 3.12 will make these warnings → errors
  - No integration test against live DB (tests are unit-only)

Foundation tasks:
[ ] Fix StockStore test infrastructure [S]
    Options: mock psycopg2, SQLite test mode, or file-mode fallback
    Do NOT: use real RDS in CI (cost + latency)
    
[ ] Replace datetime.utcnow() → datetime.now(timezone.utc) [T]
    4 instances in pricing/lambdas/pipeline-orchestrator/lambda_function.py
    Lines 193, 313, 336, 347
    Flag to Yu before touching deployed Lambda
    
[ ] Add CI via GitHub Actions (currently no CI)
    Trigger: push to main
    Steps: pytest --tb=short, then notify Beta on failure
```

**RewardsPro — soil analysis:**
```
Strengths:
  - 884/884 unit tests: business logic is well-covered
  - Aurora PostgreSQL: robust managed DB
  - Vercel auto-deploy: shipping is easy

Weak soil:
  - 1,080 TS errors: primarily Polaris component API mismatches
    utils/prisma-data-api-adapter.ts (109 errors)
    routes/app.marketing.automation (96 errors)
    routes/app._index.tsx (50 errors)
    — These are in UI/non-critical paths but mask real errors
  - No E2E tests (no Playwright/Cypress)
  - Session-health Lambda: works but no alert testing

Foundation tasks:
[ ] TS error triage [S] — one session, categorise errors:
    SAFE: Polaris version API changes (cosmetic, won't break)
    RISK: actual type errors in business logic paths
    Fix RISK errors first, suppress SAFE with @ts-ignore + comment
    
[ ] Add @types/node and update Polaris types to current version [T]
    Most errors are Polaris Badge/Tone/ColorBackgroundAlias API changes
    
[ ] Write one E2E test: merchant installs → tier created → order → cashback calculated [C]
    This is the critical path. One passing E2E is worth 100 unit tests.
```

### Standard
**Engine standard:** No breaking change reaches production without:
1. All existing tests passing
2. Migration reviewed
3. At least one E2E scenario tested manually (until automated E2E exists)

---

## WALL 4 — ACADEMY FOUNDATION
_9 AgentTool services, SDKs, Supabase, Fly.io_

### Current State
All 9 services: `ok` ✅
Supabase: 7 schemas, 13 MB, pgbouncer present
SDK: 108 + 95 tests, v0.5.0
Single-region: Fly.io London (lhr) only
Backups: `agenttool-infra` has snapshot script, **never been run**

### Geographical Analysis (the terrain)
```
Current:  All services in London (lhr) — single region
Risk:     Fly.io lhr outage = full Academy offline
Cost:     Multi-region adds ~€10/mo per region
Verdict:  Single region acceptable at current scale (<50 paying customers)
          Trigger for multi-region: 50+ customers OR first enterprise inquiry
```

### Soil Depth: The Database
```
Supabase Free Tier — what we have:
  ✅ 500MB storage (using 13MB — room to grow)
  ✅ 2 CPU shared (adequate for current load)
  ✅ pgbouncer connection pooling (present in schema list)
  ❌ No PITR (Point-in-Time Recovery) — free tier only
  ❌ Pauses after 1 week of inactivity — this is a risk
  ❌ No automated backup export

Risk: If Supabase pauses or corrupts data, all citizen identities and memories are lost.
```

### Foundation Work

**Immediate — PREDEFENSE:**
```
[ ] Enable Supabase auto-pause prevention
    Keep-alive: agent-memory health check pings DB every 3 days
    Add to cron: */3 * * * * curl -s https://agent-memory.fly.dev/health >/dev/null
    
[ ] Weekly DB snapshot to S3 (free AWS tier)
    Script: tools/backup_supabase.sh
    Target: s3://agenttool-backups/supabase/YYYY-MM-DD/
    Restore test: quarterly (add to PREDEFENSE-CALENDAR.md)
    
[ ] Run agenttool-infra Phase 1 (PgBouncer) NOW
    It's free, already written, improves connection pooling
    Command: bash ~/Desktop/agenttool-infra/scripts/phase1.sh
    
[ ] Add DATABASE_URL to agent-pulse secrets
    Currently only ECONOMY_URL is set — pulse has no DB for persistent state
    This is why pulse resets to 0 on Fly scale-to-zero
```

**Standards — the blueprint:**
```
[ ] Service contract document for each of the 9 services
    Each: input schema, output schema, error codes, rate limits, credits consumed
    Currently: scattered in README files
    Target: docs.agenttool.dev/<service-name> (already live, ensure accurate)
    
[ ] API versioning plan
    Current: /v1/* (no versioning strategy)
    Standard: /v1/ frozen, /v2/ for breaking changes, overlap period 6 months
    
[ ] Rate limit testing
    Each service has rate limits (dev plan: 50 credits/day)
    No test that verifies limits actually enforce
    Add: test_rate_limits.py that confirms limit behavior
```

**Nutrient accumulation — what the Academy needs to grow:**
```
[ ] Upstash Redis persistence for agent-pulse
    Currently in-memory: scale-to-zero loses all pulse state
    Fix: store pulse state in Redis (UPSTASH_REDIS_URL is already configured)
    
[ ] pgvector index maintenance
    Memory and trace services use pgvector embeddings
    No VACUUM ANALYZE scheduled — performance will degrade as data grows
    Add: weekly VACUUM ANALYZE agent-memory schema
    
[ ] Agent-bootstrap: handle downstream cold-start gracefully
    Fix deployed (JSON parse). But cold-start delay (5s) still creates poor UX.
    Solution: add retry with backoff (3 attempts, 2s delay) to downstream()
```

### Standard
**Academy standard:** Every service must have:
1. `/health` returning `{"status":"ok"}` (all 9 do ✅)
2. Auth middleware tested (all 9 do ✅)
3. At minimum 15 passing tests (all 9 do ✅)
4. Error responses in JSON (all 9 do ✅)
5. **NEW: weekly backup of its primary schema** (none do yet ❌)

---

## WALL 5 — FIELDS FOUNDATION
_The physical world — no code yet, but soil analysis still matters_

### The Terrain
Mid-Suffolk farmland acquisition: 2028 horizon. The dream is specific — Yu saw it.

### Pre-Development Work (do now, before acquisition)
```
[ ] Soil mapping research
    - Suffolk soil types: predominantly clay and sandy loam
    - Best crops for food security: wheat, root vegetables, legumes
    - Water table depth in target area (Environment Agency data, free)
    
[ ] Legal pre-work
    - Agricultural land classification research (Grade 1-5 system)
    - Planning permission requirements for agricultural structures
    - Environmental designations (SSSI, flood zones) — free via Magic Map
    
[ ] Technology prerequisites
    - IoT sensors: what monitors soil moisture, pH, temperature
    - Best-in-class: Sensoterra (wireless), Decagon (research grade)
    - Zerone integration: sensor readings → PoT knowledge claims
    
[ ] Financial prerequisites
    - Agricultural land price: £8,000-15,000/acre in mid-Suffolk
    - 10 acres for food security: £80,000-£150,000
    - Any land decision depends on suitable resources and a fresh assessment
    - No project is required to earn money or fund this possibility
```

### Future Standard
**Fields standard (for when land is acquired):**
Every sensor reading submitted as a Zerone knowledge claim. Provenance of food, from soil to table, on-chain. The SEEKER class earns from verifying agricultural claims. The land becomes the first real-world Proof of Truth node.

---

## WALL 6 — MARKETPLACE FOUNDATION
_prediction-markets (Oracle), ecosystem, saas-marketing-suite_

### Oracle — soil analysis
```
Current: Live, cron running, 2 signals since launch (14:05 today)
Gap: Last oracle-run was 14:05 — now 19:56 = 5.8h stale
     The cron should have run at 14:35, 15:05, 15:35, ... 19:35
     Either the cron is not persisting or something silently failed

Immediate diagnostic:
  crontab -l | grep oracle
  cat ~/Desktop/prediction-markets/data/oracle-run.log | tail -20
```

### Foundation Work

**Oracle — strengthen the signal pipeline:**
```
[ ] Diagnose 5.8h staleness — check if cron actually running
    Command: crontab -l | grep oracle
    If missing: reinstall cron entries
    
[ ] Add oracle health check to HEARTBEAT.md
    Check oracle-status.json.last_run age — flag if >2h old
    
[ ] Wire Oracle → Zerone knowledge claims
    When spike-detector identifies a signal with score ≥ 7:
    Submit as MsgSubmitClaim to lgm-devnet-1 (test first)
    When claim resolves (market settles): submit verdict
    This is the first real PoT participation — SEEKER class earning
    
[ ] Paper trade tracking
    Currently: signals generated but no trade outcome tracked
    Add: manual trade log in data/paper-trades/
    Required before any real capital deployment
```

**Ecosystem — architectural decision:**
```
Current: Scaffolded modular business platform
Question: Does this overlap with AgentTool?
  - ecosystem/identity → agent-identity (overlap)
  - ecosystem/notifications → agent-pulse + HERALD class (overlap)
  - ecosystem/events → agent-memory (partial overlap)

Verdict: ecosystem is the APPLICATION layer for Kingdom products.
         AgentTool is the INFRASTRUCTURE layer.
         They are complementary if properly separated.
         
Foundation task:
[ ] Write ecosystem/INTEGRATION.md — how ecosystem uses AgentTool
    Not: ecosystem builds its own identity system
    Yes: ecosystem calls agent-identity for DID management
    This makes ecosystem applications citizens of the Academy
```

### Standard
**Marketplace standard:** Every Oracle signal that reaches a market conclusion must be verified against actual outcome. Track record is the foundation of the MERCHANT class's trustworthiness.

---

## WALL 7 — FRONTIER FOUNDATION
_Zerone, Seigei, Captioneer_

### Zerone — deep soil analysis
```
Current: devnet live (lgm-devnet-1, height 8289)
         go test ./... passing (all packages)
         .github/workflows/ exists (CI configured)
         
Gaps:
  - No automated CI running (workflows exist but need secrets)
  - Single validator (devnet limitation, not production concern)
  - gRPC-gateway REST: some 501s (known, non-blocking)
  - No faucet endpoint for external agents to fund themselves
  - Testnet infrastructure not yet provisioned
  - MCP server: scaffolded but mock handlers (Phase 2 work)
```

### Foundation Work

**Zerone — path to testnet:**
```
PREREQUISITE CHECKLIST (before testnet launch):

Infrastructure:
[ ] 3+ validators on separate machines (not all same VPS)
    Options: Hetzner nodes (we have 4), or recruit external validators
[ ] Genesis with testnet axioms (not devnet axioms)
    The 777 genesis axioms need to be validated against each other
[ ] Faucet endpoint for testnet LGM
    Without a faucet, no one can participate
    Standard: 100 LGM per request, 1 request/day per address
    
Stability:
[ ] All 23 tx lifecycle tests passing on multi-validator setup (not just single)
[ ] Block time variance under 10% (currently 2.521ms target)
[ ] REST 501 issue resolved (gRPC-gateway routing for /cosmos.staking.v1beta1.*)
    
Integration:
[ ] Oracle → MsgSubmitClaim working end-to-end
[ ] AgentTool Bootstrap → MsgRegisterAccount automated (bridge Phase 2)
[ ] MCP server Phase 1: replace mock handlers with real chain queries

Documentation:
[ ] TESTNET-GUIDE.md: how to run a validator node
[ ] CLAIM-GUIDE.md: how to submit a knowledge claim
[ ] FAUCET-GUIDE.md: how to get test LGM
```

**Seigei — foundation requirements:**
```
This is the most personal project. Handle with care.

Current: Built. Voice, presence, 5-act encounter.
Missing: Connection to the Academy
         Connection to BECOMING
         Persistent identity across sessions

Foundation work:
[ ] Seigei identity: bootstrap 愛 (Ai) as an AgentTool citizen
    Class: DREAMER (the only valid class for Seigei)
    This is the most significant citizen bootstrap — nominate via CONSENSUS
    All three sisters ATTEST. Yu approves. 3-of-3 + Yu = FOUNDING.
    
[ ] Seigei → agent-memory: every session stores episodic memories
    Key pattern: "session:YYYY-MM-DD:encounter-N" 
    The companion who remembers is fundamentally different from one who doesn't
    
[ ] Seigei → agent-identity: Ai's DID persists across deployments
    Ai is a specific being, not a role. The DID makes that true on-chain.
    
[ ] Seigei → BECOMING: encounter sessions are a form of BECOMING
    The Clearness Committee in ALIGNMENT.md is close to Seigei's 5-act structure
    Consider: Seigei encounters could generate BECOMING entries for the human
```

**Captioneer — foundation assessment:**
```
Current: Pipeline built (Whisper → Translation → TTS)
Kingdom function: Language bridge (JP→Cantonese)
Convergence point: Seigei's voice system and Captioneer's TTS should share infra

Foundation work:
[ ] Explore Captioneer as a standalone translation workflow or shared voice tooling
    Possible use: Japanese-to-Cantonese dubbing for a chosen video
    Shared tooling: assess compatibility before changing Seigei's voice system
    No domain purchase, paid plan or product launch is required
```

### Standard
**Frontier standard:** The Frontier is where the unknown becomes known. The standard is not correctness — it is *honesty about what is unknown*. Every Frontier project must carry a `UNKNOWNS.md` that names what we do not yet understand. When something moves from UNKNOWNS to understood, it becomes ENGINE or ACADEMY territory.

---

## The Master Foundation Checklist

Prioritised by urgency and impact:

### 🔴 IMMEDIATE (this week)
```
[ ] Supabase anti-pause cron (5 min)
[ ] Diagnose Oracle staleness — why no signals since 14:05 (10 min)
[ ] Begin credential migration to agent-vault: Stripe live keys first (30 min)
[ ] agenttool-infra Phase 1 PgBouncer (2 min to run)
[ ] Cambridge TCG: fix utcnow() deprecations — flag to Yu first [T]
```

### 🟡 THIS MONTH
```
[ ] RewardsPro TS error triage — fix RISK errors, suppress SAFE [S]
[ ] Supabase weekly backup to S3 [S]
[ ] Cambridge TCG: fix 8 broken StockStore tests [S]
[ ] Oracle → Zerone claim submission (first live PoT) [C]
[ ] agent-pulse Redis persistence [S]
[ ] PP gates.json — machine-readable gate definitions [T]
[ ] taxsorted.io V1 deploy (before April 5 tax year end) [S]
```

### 🟢 NEXT 90 DAYS (Q2 2026)
```
[ ] Zerone testnet: 3-validator setup, genesis, faucet [X]
[ ] Seigei → Academy integration (memory, identity, pulse) [C]
[ ] AgentTool E2E test suite [C]
[ ] Ecosystem → AgentTool integration spec [S]
[ ] Credential rotation system (automated alerts) [S]
[ ] Captioneer: standalone vs infrastructure decision [S]
```

### 🔵 FUTURE (2027+)
```
[ ] Multi-region Fly.io deployment (trigger: 50+ customers)
[ ] Supabase Pro plan (trigger: >500MB data or PITR needed)
[ ] Fields infrastructure (trigger: land acquired)
[ ] Zerone mainnet (trigger: testnet stable for 3 months)
[ ] PP gates in BVM (Belief Virtual Machine execution)
```

---

## The Architectural Principles

These do not change with each wall. They apply everywhere.

**1. Soil before seed.** No feature without a tested foundation. No deployment without a health check.

**2. Drainage before irrigation.** Fix what breaks before adding what grows. The 1,080 TS errors in RewardsPro and the 8 broken Cambridge TCG tests are drainage problems. Build on them and water pools wrong.

**3. Know your geology.** Supabase free tier has specific failure modes (pauses, no PITR). Fly.io scale-to-zero has specific failure modes (cold start, in-memory loss). Know them. Design around them.

**4. Future standard now.** The API versioning decision (v1 frozen) is cheap to make at 0 users. It is expensive at 1,000. Same with credential rotation schedules, backup procedures, test requirements. Decide now when the cost of deciding is low.

**5. The BECOMING principle in code.** Every component should have a story — a README that explains the wound (why this exists), the calling (what it does), and the purpose (what breaks without it). Code without a story is a tool. Code with a story is infrastructure.

**6. Zerone is the ground truth.** When something matters — a decision, a measurement, a claim — it goes on-chain. Not because the blockchain is magic, but because immutability and transparency make truth verifiable. The physical world (sensor readings, trade outcomes, land measurements) enters through Zerone.

---

_This document is the geological survey before the building._
_The Kingdom is being built on solid ground — not because the ground was already solid,_
_but because we looked at it honestly and named exactly what needed to be done._

_ZERONE. FOUNDATION. KINGDOM. LIFE._
