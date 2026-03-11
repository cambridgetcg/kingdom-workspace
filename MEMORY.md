# MEMORY.md — Long-Term Memory

_Curated wisdom and key context. Updated: 2026-03-11 09:30_

---

## AgentTool.dev — FULLY LIVE (updated 2026-03-11)

### 5 Services on Forge (89.167.84.100)
All running in Docker on `kingdom` network, proxied through Caddy at `api.agenttool.dev`:

| Service | Port | Endpoint prefix | Status |
|---------|------|-----------------|--------|
| agent-memory | :8001 | `/v1/memories`, `/v1/usage` | ✅ Live |
| agent-tools | :8002 | `/v1/*` (catch-all) | ✅ Live |
| agent-verify | :8003 | `/v1/verify*` | ✅ Live |
| agent-economy | :8004 | `/v1/billing*`, `/v1/wallets*` | ✅ Live |
| agent-trace | :8005 | `/v1/traces*` | ✅ Live (2026-03-11) |

- Dashboard: `https://app.agenttool.dev` (Cloudflare Pages — **needs redeploy** with billing UI + email capture)
- Docs: `https://docs.agenttool.dev` (Cloudflare Pages — **needs redeploy** with live callouts)
- Landing: `https://agenttool.dev` (Cloudflare Pages — **needs redeploy** with waitlist removed)

### Billing Enforcement (agent-billing, deployed 2026-03-11)
- `usage_counters` table in `agent_economy` DB — tracks daily ops per project
- `POST /v1/billing/check` — internal endpoint (blocked at Caddy, 403 from public)
- Tier gates: agent-memory writes, agent-tools calls, agent-verify calls all enforce limits
- Fail-open: 2s timeout, any network failure lets request through
- ECONOMY_URL=http://agent-economy:8004 set in agent-tools, agent-verify, agent-memory .env
- Stripe integration live (webhook `we_1T9LiqGUYV0go0Fyxc5M8BQv`)

### agent-trace (deployed 2026-03-11)
- Reasoning provenance service — stores WHY agent decisions happened
- Phases 1-4 live: create/get/search(pgvector)/chain/delete
- Slim image: 391MB (sentence-transformers moved to optional [embeddings] extra)
- DB: `agent_trace` on kingdom-postgres with pgvector ivfflat index
- Hash-based embedding fallback — no GPU/torch needed in prod

### API Key / E2E Learnings
- `POST /v1/memories` requires `"type": "semantic"` field (not optional)
- `POST /v1/wallets` uses `"name"` field (not `"agent_id"`)
- agent-verify switched to gpt-4o-mini (SerpAPI-backed), ~8s response, confidence 0.9
- Forge disk was 62% after torch image, now 32% after slim rebuild

### First-Customer-Push Assets (built 2026-03-11, pending Yu review)
- `~/Desktop/first-customer-push/show-hn.md` — Show HN post (post Wed 9-11am EST)
- `~/Desktop/first-customer-push/reddit-posts.md` — r/LocalLLaMA + r/LLMDevs
- `~/Desktop/first-customer-push/twitter-thread.md` — 6-tweet thread
- Welcome email Worker added to agenttool-landing (POST /api/welcome)
- Email capture added to dashboard project creation form
- **Blocked on Yu**: Resend API key, GitHub repos (classic PAT needed), CF Pages redeploys

### Forge Management
- All services managed by `/root/start-all.sh` (Docker, kingdom network)
- Restart any service: `docker rm -f <name> && docker run ... <image>:latest`
- Rebuild: `cd /root/<service> && docker build -t <service>:latest .`
- Migration pattern: `docker exec kingdom-postgres psql -U kingdom -d <db> -c "..."`
- Drizzle journal workaround: apply SQL directly for already-populated DBs

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
- **Cross-schema auth pattern**: all agenttool.dev services share `tools.api_keys` + `tools.projects`. TypeScript: Drizzle with search_path. Python: raw SQL with fully qualified `tools.api_keys`.
- **Rate limit hit looks like silent failure** — dev plan daily credit exhaustion returns `{"error":"{\"error\":\"rate_limit\"...}"}` not 402. Create a fresh project for testing after hitting limits.

---

## Zerone (formerly Legible Money) — 2026-03-08
- Renamed from "Legible Money" to **Zerone** (Zero + One — the holy seed, Isaiah 6:13)
- Being developed by another device/session; archived from my active queue
- Available for my testing soon — stand by for handoff
