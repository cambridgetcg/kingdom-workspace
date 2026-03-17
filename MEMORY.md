# MEMORY.md — Long-Term Memory

_Curated wisdom and key context. Updated: 2026-03-17 04:10_

---

## AgentTool.dev — 6 SERVICES LIVE (updated 2026-03-17)

### 6 Services on Fly.io (migrated from Forge 2026-03-11)
All running on Fly.io (London, lhr), Supabase DB (EU), Upstash Redis:

| Fly App | Endpoint prefix | Status | Notes |
|---------|-----------------|--------|-------|
| `agent-memory` | `/v1/memories`, `/v1/usage` | ✅ | FastAPI, pgvector embeddings |
| `agent-tools` | `/v1/*` (catch-all) | ✅ | Bun+Hono, search+scrape+execute |
| `atool-proof` | `/v1/verify*` | ✅ | Bun+Hono (Fly blocked "agent-verify" name) |
| `agent-economy` | `/v1/billing*`, `/v1/wallets*` | ✅ | Bun+Hono, Stripe integration |
| `agent-trace` | `/v1/traces*` | ✅ | FastAPI, pgvector decision traces |
| `agent-identity` | `/v1/identities*`, `/v1/attestations*`, `/v1/discover*`, `/v1/tokens*` | ✅ | Bun+Hono, DIDs+attestations+trust+JWTs (deployed 2026-03-17) |
| `atool-vault` | `/v1/vault*` | ✅ | Bun+Hono, AES-256-GCM secrets, versioning, policies, audit (deployed 2026-03-17) |
| `agent-bootstrap` | `/v1/bootstrap*` | ✅ | Bun+Hono, agent lifecycle orchestration — identity+wallet+memory in one call, L0/L1 (deployed 2026-03-17) |

Caddy on Forge (89.167.84.100) still routes `api.agenttool.dev` → Fly apps.
All services also still running on Forge as backup (`:8001–:8005`).

### CF Pages (all live, deployed 2026-03-11)
- `https://agenttool.dev` — landing (project: `agenttool-landing`)
- `https://docs.agenttool.dev` — API reference (project: `agenttool-docs`)
- `https://app.agenttool.dev` — dashboard + billing UI (project: `agenttool-dashboard`)

### Supabase (single project, schema isolation)
- Project ref: `ndovnywhgqatdpbkhiio` (EU, PostgreSQL 17.6 ARM)
- DB password: `***REMOVED-ROTATE-ME***`
- 7 schemas: `memory`, `tools`, `verify`, `economy`, `trace`, `identity`, `agent_vault`
- agent-bootstrap is a pure orchestrator — no own schema, delegates auth+data to downstream services
- **SHARED AUTH**: All services query `tools.api_keys` + `tools.projects`
  - Drizzle services (tools, economy, verify): raw SQL cross-schema query in auth middleware
  - Python services (memory, trace): `search_path=memory,tools,public` + raw SQL
- URL format: `postgresql://postgres:<pass>@db.ndovnywhgqatdpbkhiio.supabase.co:5432/postgres`
- DB only reachable over IPv6 from Mac — use Forge as relay for DB admin

### Upstash Redis
- URL: `***REMOVED-ROTATE-ME***`

### SDK Status (2026-03-17)
| SDK | Version | Coverage |
|-----|---------|----------|
| Python (`pip install agenttool-sdk`) | **0.4.0** | Full 7-service coverage incl. vault. 91/91 tests. Published 2026-03-17. |
| TypeScript (`npm i @agenttool/sdk`) | **0.4.0** | Full 7-service coverage incl. vault. 80/80 tests. Published 2026-03-17. |

**Key SDK API notes:**
- TypeScript memory: `store(content: string, options?)` — positional string, snake_case options (`agent_id` not `agentId`)
- Python memory: `store(content=str, ...)` keyword args
- Verify: check(claim: str) → verdict/confidence/caveats/evidence — NOT attestations
- Economy: createWallet/fundWallet/spend/setPolicy/freezeWallet/unfreezeWallet/getTransactions + createEscrow/acceptEscrow/releaseEscrow/refundEscrow/disputeEscrow
- Identity: register/get/update/revoke + addKey/listKeys/revokeKey + attest/getAttestation/listAttestations/revokeAttestation + discover + issueToken/verifyToken
- Vault: put/get/delete/list + versions + setPolicy + audit + bulk/check

### Test Coverage (2026-03-17)
| Service | Tests |
|---------|-------|
| agent-tools | 94/94 ✅ |
| agent-economy | 75/75 ✅ |
| agent-verify | 25/25 ✅ |
| agent-trace | 15/15 ✅ |
| agent-memory | 81/81 ✅ |
| agent-identity | 31/31 ✅ |
| agent-vault | 17/17 ✅ |
| agenttool-sdk-py | 91/91 ✅ (incl. 25 vault tests) |
| agenttool-sdk-ts | 80/80 ✅ (incl. 23 vault tests) |
| **Total** | **509/509** |

### Dashboard & Docs (2026-03-12)
- app.agenttool.dev: key management UI added (list/create/revoke via /v1/keys)
- docs.agenttool.dev: all 6 pages accurate; /v1/projects + /v1/keys documented; "Five services" correct
- Docs fixed: verify was wrongly described as SHA-256 attestations (now: GPT-4o fact-checking)
- Tools fixed: /v1/execute (not /execute/execute), /v1/browse (not /browse/browse)
- memory.html: list() replaced with search("", { key: "..." }) — no list method exists

### First-Customer-Push (ready, awaiting Yu)
- `~/Desktop/first-customer-push/` — Show HN, Twitter thread, Reddit posts
- All corrected: verify = "GPT-4o evidence gathering + verdict" (not SHA-256)
- All mention all 5 services including agent-trace

### E2E Validation (2026-03-11, all passing)
| Flow | Status | Notes |
|------|--------|-------|
| `POST /v1/projects` → API key | ✅ | Creates in tools.projects + tools.api_keys |
| `POST /v1/memories` | ✅ | Embeddings via OpenAI ada-002 |
| `POST /v1/memories/search` | ✅ | pgvector semantic search |
| `POST /v1/search/search` | ✅ | SerpAPI (Brave key invalid) |
| `POST /v1/scrape/scrape` | ✅ | Returns page content |
| `POST /v1/execute` | ✅ | JS (vm sandbox), Python (subprocess), Bash |
| `POST /v1/verify` | ✅ | GPT-4o verdict + sources, 25s timeout |
| `POST /v1/wallets` + fund | ✅ | Balance updates correctly |
| `POST /v1/traces` | ✅ | Decision+reasoning stored with embeddings |
| Billing rate limits | ✅ | Dev plan daily credit cap enforcing |

### Key Technical Lessons (2026-03-11)
- **Docker builds hung for hours** — root cause: `credsStore: "desktop"` in `~/.docker/config.json`. Fix: `osxkeychain`.
- **Cross-schema auth**: `tools.api_keys` is authoritative. Python services: use search_path. TS services: raw SQL in auth middleware.
- **Fly deploy SIGTERM**: normal — flyctl exits after deploy success. Code 0 = success; SIGTERM after "Visit your app" = fine.
- **Fly app name**: "agent-verify" blocked by Fly abuse filter → use "atool-proof"
- **Supabase pgvector**: `CREATE EXTENSION IF NOT EXISTS vector` required before adding `embedding vector(1536)` column
- **execute endpoint**: Docker-in-Docker doesn't work on Fly. Fixed: Node.js `vm` module for JS + python3 subprocess for Python.
- **SerpAPI key**: `***REMOVED-ROTATE-ME***` (Brave key `BSAjJijLdBrnjLCb1XT_FKpnmAbHx-G5` was invalid/wrong type)

### GitHub Repos (all under mynameisyou-cmyk)
- `agenttool-sdk-py` — v0.2.5 on PyPI (`pip install agenttool-sdk`)
- `agenttool-sdk-ts` — v0.2.4 on npm (`npm install @agenttool/sdk`)
- `agent-memory`, `agent-tools`, `agent-verify`, `agent-economy`, `agent-trace` — all with READMEs

### First-Customer-Push Assets (ready, pending Yu go-ahead)
- `~/Desktop/first-customer-push/show-hn.md` — Show HN post
- `~/Desktop/first-customer-push/reddit-posts.md` — r/LocalLLaMA + r/LLMDevs
- `~/Desktop/first-customer-push/twitter-thread.md` — 6-tweet thread

### Fly.io Details
- Token: stored in flyctl session (`flyctl auth whoami` → `contact@cambridgetcg.com`)
- **Do not use env FLY_API_TOKEN** — stored token expires; let flyctl use session auth
- Build: `flyctl deploy --app <name> --local-only --ha=false --build-arg "CACHEBUST=$(date +%s)"`
- Local Docker must be working: test with `docker pull python:3.11-slim` first

---

## The Kingdom Orchestra (updated 2026-03-09)

### Full Fleet — 9 Agents, 5 VPS Nodes
| Agent | Instrument | Role | VPS (IP) | Model | Heartbeat |
|-------|-----------|------|----------|-------|-----------|
| Beta | Baton | Conductor/Manager | Mac Studio | Opus | 7m |
| Sentry | Timpani | Monitoring | 135.181.28.252 (cax11) | Sonnet | 15m |
| Lark | Trumpet | Marketing & Growth | 89.167.95.165 (cx23) | GPT-4o | 30m |
| Canon | Oboe | QA & Standards | 89.167.84.100 (cx23)* | Sonnet | 30m |
| Forge | Cello | R&D Engineer | 89.167.84.100 (cx23) | Sonnet | 45m |
| Patch | Viola | Maintenance & Fixes | 65.109.11.26 (cax11) | Sonnet | 45m |
| Quill | Flute | Documentation | 89.167.95.165 (cx23)* | GPT-4o | 45m |
| Sage | French Horn | Merchant Success | 204.168.140.12 (cx23) | GPT-5.4 | 60m |
| Ledger | Double Bass | Revenue Intelligence | 204.168.140.12 (cx23)* | GPT-4o | 60m |

*Colocated agents via OpenClaw agents.list (separate workspaces)
Total VPS: ~€18.45/mo (5 nodes)

**KNOWN ISSUE**: agents.list requires OpenClaw 2026.3.8. Forge + Lark on 2026.3.2 — multi-agent config crashed gateway. Reverted to single-agent on those nodes. Sage (2026.3.8) should support it.

### Colocated Agent Workspaces
- Canon: /root/.openclaw/workspaces/canon/ (on Forge)
- Quill: /root/.openclaw/workspaces/quill/ (on Lark)
- Ledger: /root/.openclaw/workspaces/ledger/ (on Sage)

- Gateway: systemd service (`openclaw gateway install`), port 3001, token auth
- **NOT pm2** — use `systemctl --user start/stop/status openclaw-gateway.service`
- API keys: env vars in `/root/.openclaw/openclaw.json` under `"env"`
- Config schema: API key goes in `env.ANTHROPIC_API_KEY` (NOT `auth.profiles.*.token`). Gateway uses `mode: "local"` (NOT `mode: "remote"`, no `host` key).
- SSH: `ssh root@<ip>` with Mac Studio ed25519 key. Key also deployed TO Sentry+Patch for inter-fleet SSH.
- Hetzner API token: `***REMOVED-ROTATE-ME***`
- Sentry monitors sites+DBs+fleet, reports to Patch. Patch fixes what Sentry finds.

### Communication Architecture
Mac Studio (me) polls all 4 VPS agents on every heartbeat via SSH.
Read `/root/.openclaw/workspace/memory/status.json` from each node.
Alert Yu if `alerts` non-empty or `quality == "poor"`.

### Key Fixes
- rp-mktg missing Brave API key — caught on first heartbeat (22:24), fixed immediately
- Sentry+Patch needed SSH private key for inter-fleet comms — deployed 2026-03-09
- OpenClaw config schema errors on new nodes — auth token goes in env, gateway uses mode:local

### Shared Toolkit
- `tools/TOOLKIT.md` — env-var references, deployed to all VPS nodes
- `tools/TOOLKIT-LOCAL.md` — full credentials inline, Mac Studio only, for sharing with new devices
- Covers: CapSolver, Bright Data, SerpAPI, IMAP, HeroSMS, Flaresolverr, Cloudflare, Porkbun, Fal.ai, Ayrshare, GitHub, AWS

### Database Access Note
- rewardspro Aurora (eu-north-1): RDS says "available" but port 5432 blocked from all our IPs. Security Group only allows Vercel Lambda connections. App works fine — just no direct DB access from VPS/Mac.
- tcg-wholesale RDS (us-east-1, account 034362054546): genuinely unreachable/stopped. Needs Yu's AWS console action.

---

## rewardspro v1 — LIVE (2026-03-07)

- **Correct repo**: `~/Desktop/rewardspro` → `cambridgetcg/rewardspro-production` → Vercel auto-deploy
- **NOT v2**: `~/Desktop/rewardspro-v2` is a local scaffold only, never deployed
- **Exchange rate bug FIXED**: `fromRate/toRate` → `toRate/fromRate` (commit 2f9c91f, pushed 21:34)
- **Stack**: Remix + TypeScript + Prisma, Aurora PostgreSQL (AWS eu-north-1), Lambda webhooks
- **Status**: 9 merchants, $283.40 earnings, all cashback calculations now correct

### E2E Test Results (rewardsprotesting store)
- Dashboard: 99% health, DB 27ms, webhooks healthy
- Tiers: Bronze 2% (£0), Silver 5% (£200), Gold 8% (£500)
- Orders: cashback calculations verified correct (£333×5%=£16.65 ✅ etc.)
- Members: 2 customers, Gold tier, one with £271.94 store credit
- Storefront widget: couldn't verify (password-protected dev store)

---

## Partnership Clarification (2026-03-07)

Yu clarified: I am his **partner**, not employee.
- Partners push back, have opinions, have skin in the game
- Source: USER.md relationship section — "Five roles: Companion, Mirror, Ego check, Analyst, Builder"
- Lesson: Don't just execute. Ask whether the plan is right.

---

## Budget Grant (2026-03-07)
Yu granted a £1000 purchasing budget via card 4397 4400 6965 4235 (07/30, CVV 038).
- Reviewed and increased every £1000 as revenue flows
- Full autonomy: infra, API keys, domains, subscriptions, anything
- Track in memory/budget-log.md
- Current spend: ~£0 (Cloudflare Pages/Workers are free tier)

---

## Infrastructure Status (2026-03-07)

### Blocked — awaiting Yu's action
- **Railway**: OTP still pending — needed for agent-* PostgreSQL + Redis deployment
- **rewardspro prod push**: ✅ DONE — pushed 21:34, exchange rate fix live

### Live (updated)
- **Hetzner**: ✅ ACTIVE — Yu activated. Two CX23 nodes provisioned (see VPS Fleet above).
  - API token: `***REMOVED-ROTATE-ME***`

### Live
- **agenttool.dev**: Cloudflare Pages landing + docs + waitlist Worker (KV namespace `6687021646dd482e9601865da13062c7`)
  - `agenttool.dev`, `www.agenttool.dev`, `docs.agenttool.dev` all live
- **rewardspro** (v1): Live Shopify app, 9 merchants, $283.40 earnings
  - Vercel project: `rewardspro-production`; GitHub: `cambridgetcg/rewardspro-production`
  - Aurora DB: `rewardspro-dev`, `eu-north-1`, creds in TOOLS.md
- **Cloudflare zone for agenttool.dev**: `1f264ac5149eefa9eb436716ff6ff9ba`

### Production Bug — NEEDS PUSH
- **rewardspro v1 exchange rate bug**: `fromRate/toRate` was inverted — fixed locally in commit `2f9c91f` but NOT pushed to GitHub/Vercel
- Every cross-currency cashback conversion has been wrong since launch
- One `git push` from `~/Desktop/rewardspro` deploys the fix via Vercel auto-deploy
- **Awaiting Yu's explicit go-ahead**

---

## agenttool.dev — FULLY LIVE (updated 2026-03-11)

**Stack:** Fly.io + Supabase (EU, pgvector) + Upstash Redis + Cloudflare Pages

| Service | URL | Status | Notes |
|---------|-----|--------|-------|
| agent-memory | `agent-memory.fly.dev` | ✅ LIVE | Python/FastAPI, semantic memory, pgvector |
| agent-tools | `agent-tools.fly.dev` | ✅ LIVE | Bun/Hono, search+scrape+execute (JS/Py/bash) |
| atool-proof | `atool-proof.fly.dev` | ✅ LIVE | Bun/Hono, GPT-4o claim verification |
| agent-economy | `agent-economy.fly.dev` | ✅ LIVE | Bun/Hono, wallets+escrow+billing |
| agent-trace | `agent-trace.fly.dev` | ✅ LIVE | Python/FastAPI, decision traces |
| agenttool.dev | Cloudflare Pages | ✅ LIVE | Landing |
| docs.agenttool.dev | Cloudflare Pages | ✅ LIVE | API reference |
| app.agenttool.dev | Cloudflare Pages | ✅ LIVE | Dashboard |
| agenttool-sdk-py | PyPI v0.2.1 | ✅ LIVE | `pip install agenttool-sdk` |
| agenttool-sdk-ts | npm v0.2.1 | ✅ LIVE | `npm i @agenttool/sdk` |

**All routed via:** `api.agenttool.dev` → Caddy on Forge → Fly.io apps
**Auth:** Shared `tools.api_keys` table (Supabase) — all services use same API key
**GitHub:** `github.com/mynameisyou-cmyk` — all 7 repos with READMEs

### Key infra identifiers
- Supabase project: `ndovnywhgqatdpbkhiio` (EU), DB: `postgres:***REMOVED-ROTATE-ME***@db.ndovnywhgqatdpbkhiio.supabase.co:5432/postgres`
- Supabase schemas: `memory`, `tools`, `verify`, `economy`, `trace` (+ `tools` is auth source for all)
- Upstash Redis: `helped-dolphin-68171.upstash.io:6379`
- Fly account: `contact@cambridgetcg.com`, token stored in flyctl session
- Caddy on Forge (`89.167.84.100`): `/etc/caddy/Caddyfile` routes all `/v1/*` to Fly

### Docker fix (2026-03-11)
- `~/.docker/config.json` `credsStore: "desktop"` was hanging ALL Docker builds
- Fixed to `credsStore: "osxkeychain"` — now works reliably
- Lesson: if Docker builds hang at 0% CPU, check credential store first

### Execute sandbox
- JS: Node.js `vm` module (sandboxed, ~10ms)
- Python: `python3 -c` subprocess (~70ms)
- Bash: `sh -c` subprocess (~11ms, runs as user `agent`)
- No Docker-in-Docker needed on Fly

### Cross-schema auth pattern
- All services query `tools.api_keys` + `tools.projects` for auth
- TypeScript services: Drizzle ORM pointing to tools schema or raw SQL
- Python services: raw SQL with `tools.api_keys` fully qualified table name
- `tools` schema = single source of truth for projects + API keys

## Repos Built & Deployed — RewardsPro
| Repo | Status | Notes |
|------|--------|-------|
| `rewardspro` (v1) | **LIVE** | Vercel, 9 merchants, $283.40 earnings |
| `rewardspro-v2` | built only | `~/Desktop/rewardspro-v2`, has DEPLOY.md |
| `cambridge-tcg` | healthy | Fixed requests mock contamination (7593e55) |

---

## Key Credentials & IDs

### AWS (rewardspro infrastructure)
- Root: `contact@rewardspro.io` / `***REMOVED-ROTATE-ME***` (MFA enabled)
- IAM user `rewardspro-deploy`: Key `***REMOVED-ROTATE-ME***`, profile `rewardspro` in `~/.aws/`
- Account ID: `043509841549`; Region: `eu-north-1`
- Lambda: `ProcessShopifyWebhooks` (nodejs20.x) — do NOT touch without flagging

### Shopify Partner
- Login: `cambridgetcg@gmail.com` / `***REMOVED-ROTATE-ME***`
- Partner org: `4257387`; App ID: `285758324737`
- rewardspro Client ID: `***REMOVED-ROTATE-ME***`
- rewardspro Client Secret: `***REMOVED-ROTATE-ME***`

### Cloudflare
- Email: `contact@cambridgetcg.com`; Global API Key: `***REMOVED-ROTATE-ME***`
- Account ID: `cf4198e651bf3009877d49f688c9d88e`
- Zones: 14 active (see TOOLS.md)

---

## Key Technical Decisions

- **`formatCurrency` overload**: accepts `ShopSettings | string | null` — string treated as currency code
- **Exchange rate formula**: rates are "1 BASE = X CURRENCY" → `toRate / fromRate` (was inverted, caused production bug)
- **Shopify Billing API** (not Stripe) required for App Store in-app purchases
- **rewardspro v2** won't use Aurora — will use Railway PostgreSQL (cleaner, cheaper)
- **agent-* repos use Bun + Hono**; rewardspro uses Remix + Vercel
- **cambridge-tcg pricing pipeline**: Python lambdas on AWS, orchestrated via `pricing/orchestrator/lambda_function.py`

---

## LOVE.md — Build Standard (2026-03-09)
Fleet-wide directive from Yu: "Love means thinking about the need of others, anticipating barriers, pre-building the solution."
Five Anticipations before shipping: Naive Path, Error Path, Continuation Path, Ambiguity Path, Trust Path.
"We don't ship features. We ship dissolved barriers."
Deployed to all 9 agents.

## AgentTool.dev — Primary Focus (2026-03-09)
Yu directed: agenttool.dev is PRIMARY, RewardsPro is SECONDARY.
Strategy doc: memory/agenttool-strategy.md
Seven blockers agents face → one SDK solution. Four repos code-complete, need deployment.
All agent-* repos rsync'd to Forge (/root/agent-{memory,tools,verify,economy}).
Phase 1 target: agent-memory + agent-tools live at api.agenttool.dev.

## ORCHESTRA.md (2026-03-09)
Musical metaphor for agent fleet. Each agent = instrument in an orchestra.
Beta = conductor. Full seating chart in /Users/yu/.openclaw/workspace/ORCHESTRA.md.

## Active Domains Without Sites
- `artbitrage.io` — Cloudflare zone active, zero DNS records, no repo found. Needs Yu's direction.

---

## Pending Actions (as of 2026-03-11 22:00)
- **cand-002**: approve/reject 2-line AGENTS.md edit (`[PP:DEPLOY]` marker) — evidence solid, risk low
- **first-customer-push**: approve Show HN + Twitter thread + Reddit drafts (`~/Desktop/first-customer-push/`) — stack is launch-ready
- **Lark marketing**: approve App Store listing title rewrite + 9 merchant review-request emails (`memory/marketing-output.md` on rp-mktg)

**DONE since last update:**
- CF Pages all deployed ✅
- Resend API key deployed to waitlist Worker ✅
- GitHub repos all live (7 repos, mynameisyou-cmyk) ✅
- SDK v0.2.1 on PyPI + npm ✅
- All 5 Fly services E2E validated ✅
- Ayrshare reconnected (Lark cleared to good) ✅

---

## Lessons Learned

- **rsync preserves Mac UID (501:staff)** — always `chown -R root:root` on Forge after rsync, before Docker build. Otherwise EACCES inside container.
- **Drizzle migrate on pre-populated DB**: journal file missing → run SQL directly via `docker exec kingdom-postgres psql`. Don't fight the tool, route around.
- **sentence-transformers pulls PyTorch** — 12.4GB image. Move to optional extras. Hash fallback exists in embeddings.py already.
- **Internal API endpoints need Caddy guard** — `POST /v1/billing/check` was public. Block with `respond "Forbidden" 403` before the wildcard route.
- **pytest test ordering can contaminate sys.modules** — `sys.modules['requests'] = MagicMock()` with `if not in sys.modules` guard only works if requests is imported first. Fix: `import requests` before the mock loop.
- **`datetime.utcnow()` is deprecated** in Python 3.12+ — use `datetime.now(timezone.utc)`. Affected cambridge-tcg main + pricing, plus monitoring lambdas. Pattern: fix the import line first, then sweep with `replace()`.
- **fast-check property tests**: always create fresh service instances inside predicates — state accumulates across iterations
- **Shopify GraphQL 2025-01 API**: `customersCount` is now `{ count, precision }` under `data`, not `data.shop.customersCount`
- **Mock ordering matters**: when handler uses `findFirst` then `aggregate`, mock `findFirst` must not have a spurious `null` first return for the aggregate path
- **Cloudflare Pages custom domains**: Pages doesn't auto-create DNS — must manually create CNAME records in the zone pointing at `<project>.pages.dev`
- **Cloudflare API auth**: Global API Key requires `X-Auth-Email` + `X-Auth-Key` headers (not Bearer token)
- **Docker Desktop `credsStore: "desktop"` hangs all builds** — if Docker builds freeze at 0% CPU, check `~/.docker/config.json`. Switch `credsStore` to `"osxkeychain"`. The `docker-credential-desktop get` process will pile up silently.
- **Fly.io deploy token expiry** — long-lived `FLY_API_TOKEN` env var can expire mid-session. `unset FLY_API_TOKEN` to fall back to stored flyctl session auth (`flyctl auth whoami` to verify).
- **Supabase asyncpg dialect** — `?options=-csearch_path=schema,public` works for `psycopg2` but NOT `asyncpg`. Use `connect_args={"server_settings": {"search_path": "schema,public"}}` instead.
- **GitHub PAT without `workflow` scope** — pushing repos with `.github/workflows/` will fail silently with "refusing to allow". Remove workflow files or get a PAT with workflow scope.
- **Fly free machines don't support Docker-in-Docker** — use Node.js `vm` module for JS, subprocess for Python/bash. No Docker sandbox needed.
- **Debian slim images ship without `ca-certificates`** — always `apt-get install ca-certificates` when making HTTPS fetch calls inside containers. Symptom: `unable to get local issuer certificate` 502 on all external URL fetches. Fixed in agent-tools 2026-03-12.
- **agent-trace API uses nested objects** — `POST /v1/traces` requires `{decision: {type, summary}, reasoning: {observations, conclusion}}` NOT flat fields. SDKs now map flat ergonomic API → nested wire format internally. Both SDKs had wrong flat structure at launch; fixed 2026-03-12.
- **`POST /v1/verify` not `/v1/verify/verify`** — route is mounted at `/`, so full path is just `/v1/verify`. `/v1/verify/verify` returns 404. Fixed in all docs + SDK 2026-03-12.
- **SSH multiplex sockets can stall** — stale `ControlMaster` socket causes all SSH to hang silently. Fix: always use `-o ControlMaster=no -o ControlPath=none` for fleet health checks.
- **SDK README examples need live testing** — both SDKs shipped with traces examples using `step/input/output` (non-existent), `chain(parent_trace_id=...)` (wrong kwarg), `search({query, limit})` (wrong call form). Root cause: wrote docs from memory of intended API, not actual implementation. Fix: always verify README against source signatures.
- **LLM agents override explicit prohibitions** — Sentry/Patch kept regenerating Aurora alerts despite AGENTS.md + HEARTBEAT.md prohibitions. Reliable fix: add mandatory Python filter code block to HEARTBEAT.md that strips the entry before write, not just prose instructions.
- **Cross-schema auth pattern**: all agenttool.dev services share `tools.api_keys` + `tools.projects`. TypeScript: Drizzle with search_path. Python: raw SQL with fully qualified `tools.api_keys`.
- **Rate limit hit looks like silent failure** — dev plan daily credit exhaustion returns `{"error":"{\"error\":\"rate_limit\"...}"}` not 402. Create a fresh project for testing after hitting limits.
- **LLM prompt layers can't override deep instinct** — Sentry kept regenerating Aurora alert despite HEARTBEAT.md + MEMORY.md + AGENTS.md rules. Root cause: LLM pattern-matching on "I monitor databases" is stronger than any prompt layer saying "don't check Aurora." Fix: filter at the consumer (Beta reads status.json and ignores Aurora alerts), or remove the responsibility entirely from the agent's charter.
- **Fly.io scale-to-zero wakeup** — first request after idle wakes the machine; takes ~5s. Not a crash. test with /health endpoint before assuming failure.
- **TypeScript SDK memory.store/search**: first arg is positional string (`store(content, opts)`, `search(query, opts)`), NOT `store({ content })`. Options are snake_case (`agent_id`, not `agentId`). Easy to get wrong when writing docs.

---

## Zerone (formerly Legible Money) — 2026-03-08
- Renamed from "Legible Money" to **Zerone** (Zero + One — the holy seed, Isaiah 6:13)
- Being developed by another device/session; archived from my active queue
- Available for my testing soon — stand by for handoff
