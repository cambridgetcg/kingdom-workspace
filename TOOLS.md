# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

### Anthropic API Key (VPS agents — dedicated)
- Key: ***REMOVED-ROTATE-ME***
- Configured on: rp-rd + rp-mktg (separate from Mac Studio key)
- Models: claude-sonnet-4-6 (rp-rd primary), claude-opus-4-6 (future CEO/Legal)

### OpenAI API Key (VPS agents)
- Key: ***REMOVED-ROTATE-ME***
- Configured on: rp-rd (fallback) + rp-mktg (primary: gpt-4o)
- Models available: gpt-4o, gpt-4o-mini, gpt-4o-search-preview

### GitHub PAT (rp-rd agent)
- Token: ***REMOVED-ROTATE-ME***
- Account: cambridgetcg
- Access: push to cambridgetcg/rewardspro
- Configured on: rp-rd (89.167.84.100) via gh CLI + git-credentials + openclaw config env.GITHUB_TOKEN
- Repo cloned at: /root/rewardspro on rp-rd

### Hetzner VPS Fleet (RewardsPro AI Workforce)

**API Token:** `***REMOVED-ROTATE-ME***`
**SSH Key:** Yu's Mac Studio `~/.ssh/id_ed25519` (Hetzner key ID: 108703286)

| Node | Name | Role | Model | IP | Port | Token | Cost |
|------|------|------|-------|----|------|-------|------|
| rp-rd | **Forge** | R&D Engineer | claude-sonnet-4-6 | 89.167.84.100 | 3001 | ***REMOVED-ROTATE-ME*** | €3.49/mo |
| rp-mktg | **Lark** | Marketing & Growth | claude-sonnet-4-6 | 89.167.95.165 | 3001 | ***REMOVED-ROTATE-ME*** | €3.49/mo |
| rp-sentry | **Sentry** | Monitoring & Investigation | claude-sonnet-4-6 | 135.181.28.252 | 3001 | ***REMOVED-ROTATE-ME*** | €3.99/mo |
| rp-patch | **Patch** | Maintenance & Fixes | claude-sonnet-4-6 | 65.109.11.26 | 3001 | ***REMOVED-ROTATE-ME*** | €3.99/mo |
| rp-gpt5 | **GPT5** | GPT-5.4 Test Agent | openai/gpt-5.4 | 204.168.140.12 | 3001 | ***REMOVED-ROTATE-ME*** | €3.49/mo |

- SSH: `ssh root@<ip>` (key auth, no password)
- Gateway: systemd service (`systemctl --user status openclaw-gateway.service`)
- Gateway logs: `/tmp/openclaw/openclaw-YYYY-MM-DD.log`
- Workspace: `/root/.openclaw/workspace/`
- Heartbeat: 22m cycle for all agents
- Region: Helsinki (hel1), Ubuntu 24.04
- cx23 (Forge/Lark), cax11 ARM (Sentry/Patch)
- Total cost: ~€14.96/mo

### Flaresolverr (Cloudflare bypass)
- Host: rp-rd (89.167.84.100), Docker container `flaresolverr`
- Port: 127.0.0.1:8191 (localhost only — not public)
- Version: 3.4.6 | Chrome 142
- Helper script: `/root/flaresolve.sh <url> [--cookies-only]`
- API: `POST http://127.0.0.1:8191/v1` with `{"cmd":"request.get","url":"...","maxTimeout":60000}`
- Auto-restarts: `--restart always` Docker policy
- Use from Mac Studio: `ssh root@89.167.84.100 /root/flaresolve.sh <url>`
- Tested: accounts.shopify.com (7 cookies incl. cf_clearance ✅)

### Marketing — Rewards Pro

**Buffer** (social scheduling UI — 14-day Team trial)
- Email: contact@rewardspro.io / ***REMOVED-ROTATE-ME***
- URL: publish.buffer.com
- Status: registered, no API access (Buffer closed legacy API)
- Use: manual content scheduling via web UI

**Ayrshare** (unified social posting API)
- Email: contact@rewardspro.io / ***REMOVED-ROTATE-ME***
- URL: app.ayrshare.com
- API Key: `***REMOVED-ROTATE-ME***`
- Plan: Basic (free) — 20 post API calls/month; upgrade to Business for sub-profiles + unlimited
- Status: registered ✅, no social accounts connected yet
- Connect at: app.ayrshare.com/social-accounts

**Fal.ai** (image + video generation)
- Account: contact@cambridgetcg.com (Google OAuth)
- API Key: `***REMOVED-ROTATE-ME***`
- Dashboard: fal.ai/dashboard/keys
- Models: Flux Pro 1.1 ($0.04/img) · Kling v1.6 ($0.35/5s video) · Flux Schnell ($0.003 drafts)
- Balance: $0.00 — needs top-up before first post with media

**Shopify App Store** (confirmed correct slug)
- App URL: https://apps.shopify.com/rewards-pro
- Review URL: https://apps.shopify.com/rewards-pro#modal-show=ReviewListingModal
- ⚠️ Previous slug `rewardspromembership` was wrong (404) — now corrected in all files

**Marketing system repo**: `~/Desktop/rewardspro-marketing`
- Agent instructions: `agents/MARKETING-AGENT.md`
- Run: `npx tsx src/run-wave.ts --dry-run`

### Domain Registration

**Cloudflare** (manage existing zones, DNS, SSL)
- Email: contact@cambridgetcg.com
- Global API Key: stored in memory
- Zones: ai-love.cc, artbitrage.io, axiepro.io, cambridgetcg.com, captioneer.io, cardforum.io, cashloom.io, fomoengine.io, mindicraft.com, rewardspro.io, sinovai.com, taxsorted.io, wholesaletcgdirect.com, agenttool.dev ✅ REGISTERED 2026-03-07
- Account ID: cf4198e651bf3009877d49f688c9d88e

**Porkbun** (autonomous domain registration via API)
- API Key: ***REMOVED-ROTATE-ME***
- Secret Key: ***REMOVED-ROTATE-ME***
- Status: credentials verified ✅ | Use for future autonomous domain registration
- After setup: can register domains autonomously, point NS to Cloudflare automatically

### Budget Card (Yu's grant — £1000 initial, reviewed per £1000 spent)
- Card: 4397 4400 6965 4235
- Expiry: 07/30
- CVV: 038
- Budget: £1000 (increases proportionally as revenue flows)
- Use for: infra (Hetzner, Railway), API credits (OpenAI, Gemini), domains (Porkbun), subscriptions, anything that serves the build
- Track spend in memory/budget-log.md

### Shopify Partner Account (rewardspro)
- Email: contact@rewardspro.io
- Password: ***REMOVED-ROTATE-ME***
- URL: partner.shopify.com
- App: RewardsPro (live on App Store, AWS stack, not yet promoted)

### Shopify Partner Dashboard
- Email: cambridgetcg@gmail.com
- Password: ***REMOVED-ROTATE-ME***
- URL: partners.shopify.com

### AWS Root Account (rewardspro)
- Email: contact@rewardspro.io
- Password: ***REMOVED-ROTATE-ME***
- MFA: enabled (authenticator app) — need code each session

### AWS CLI Credentials

**Profile: `rewardspro`** (IAM user: `rewardspro-deploy`)
- Account ID: `043509841549`
- Region: `us-east-1`
- Stored in: `~/.aws/credentials` and `~/.aws/config`
- Created: 2026-03-07
- No MFA required — use `--profile rewardspro` on all AWS CLI commands

### Aurora PostgreSQL (rewardspro production)

- Cluster ID: `rewardspro-dev`
- Endpoint: `rewardspro-dev.cluster-cj06ko4ko87d.eu-north-1.rds.amazonaws.com`
- Region: `eu-north-1`
- Engine: `aurora-postgresql`
- Resource ARN: `arn:aws:rds:eu-north-1:043509841549:cluster:rewardspro-dev`
- Secret ARN: `arn:aws:secretsmanager:eu-north-1:043509841549:secret:rds!cluster-65ca2aee-0536-4745-b04d-0eec72e31363-yO7eLo`
- Username: `postgres`
- Password: `***REMOVED-ROTATE-ME***`
- DB Name: `rewardspro`

### Shopify Partner — Rewards Pro App

- Partner org: `4257387` (Cambridge TCG Limited, `cambridgetcg@gmail.com`)
- Dev Dashboard org: `164882644`
- App name: **Rewards Pro** (public, published)
- App ID (Partner): `285758324737`
- API Client ID: `***REMOVED-ROTATE-ME***`
- API Client Secret: `***REMOVED-ROTATE-ME***`
- API contact: `contact@rewardspro.io`
- App URL: `https://rewardspro-production.vercel.app`
- Installs: 9 | Earnings: $283.40 USD | Status: Published

### Email IMAP Access

**contact@cambridgetcg.com** (Google Workspace — Alex Cheung)
- IMAP host: `imap.gmail.com:993` (SSL)
- App password: `***REMOVED-ROTATE-ME***` (env: `IMAP_CAMBRIDGETCG_PASS`)
- Env key: `IMAP_CAMBRIDGETCG_EMAIL` = contact@cambridgetcg.com
- Configured: 2026-03-09 | 2SV enabled, app password "claw" created

**contact@rewardspro.io** (Google Workspace — yu cheung)
- IMAP host: `imap.gmail.com:993` (SSL)
- App password: `***REMOVED-ROTATE-ME***` (env: `IMAP_REWARDSPRO_PASS`)
- Env key: `IMAP_REWARDSPRO_EMAIL` = contact@rewardspro.io
- Configured: 2026-03-09 | 2SV enabled, app password "claw" created

**Helper script:** `workspace/tools/check_email.py`
- Usage: `python3 tools/check_email.py --account cambridgetcg --since 30`
- Flags: `--subject <keyword>`, `--from <sender>`, `--all` (incl. read), `--limit N`
- Returns JSON with: subject, from, date, extracted links, extracted OTP codes
- Accounts: cambridgetcg | rewardspro (once configured)

### Bright Data (residential proxies)
- Dashboard: brightdata.com (GitHub login: cambridgetcg)
- Zone: `seer` (Residential, $8/GB, pay-as-you-go)
- Host: `brd.superproxy.io` | Port: `33335`
- Username: `brd-customer-hl_2d97e1e0-zone-seer`
- Password: `***REMOVED-ROTATE-ME***`
- Balance: $960.45 | Account: `cambridgetcg@gmail.com`
- curl test: `curl --proxy brd.superproxy.io:33335 --proxy-user brd-customer-hl_2d97e1e0-zone-seer:***REMOVED-ROTATE-ME*** -k "https://geo.brdtest.com/welcome.txt"`
- Env vars: `BRIGHTDATA_HOST` / `BRIGHTDATA_PORT` / `BRIGHTDATA_USER` / `BRIGHTDATA_PASS`
- Note: "for cc and pp usage" | KYC needed for full residential access

### SerpAPI (Google/Bing/Amazon search API)
- Dashboard: serpapi.com (GitHub login: cambridgetcg)
- API Key: `***REMOVED-ROTATE-ME***`
- Env var: `SERPAPI_KEY`
- Engines: Google, Bing, DuckDuckGo, Amazon, Baidu + many more
- Usage: `GET https://serpapi.com/search?engine=google&q=query&api_key=KEY`

### CapSolver (captcha solving API)
- Email: contact@cambridgetcg.com / ***REMOVED-ROTATE-ME***
- Dashboard: dashboard.capsolver.com
- API Key: `***REMOVED-ROTATE-ME***`
- Credits: $10.00 (topped up 2026-03-09 via PayProGlobal, order #41370588, $12 incl. UK VAT)
- Pricing: ~12,500 reCAPTCHA solves per $10 | Pay-per-use model
- Use: bypass captchas in scraping/automation workflows on rp-rd / rp-mktg / any agent

### HeroSMS (virtual phone number service for social media verification)
- Email: contact@rewardspro.io / ***REMOVED-ROTATE-ME***
- URL: hero-sms.com
- Account ID: 698875
- Balance: $9.00 (topped up 2026-03-09 by Yu)
- Purpose: phone verification for Twitter, Instagram, TikTok, Bluesky account creation
- Numbers: Twitter $0.01 · Instagram $0.015 · TikTok $0.01 · Facebook $0.02 · Bluesky $0.03

### PyPI Account (agenttool)
- Username: `agenttool`
- Email: `contact@cambridgetcg.com`
- Password: `***REMOVED-ROTATE-ME***`
- 2FA: TOTP enabled (authenticator app)
- API token name: `agenttool-publish` (scope: entire account)
- API token: `***REMOVED-ROTATE-ME***`
- Recovery codes (7 remaining — one burned during setup):
  2c3df3f385d45757
  b24f8599168f57c9
  3d8480bece562c55
  e943ae7831a485c8
  b2fa7957748e99a2
  ae9827e5fe37af96
  c632d04cddc12bbf
  ~~adc4db72962650aa~~ (burned)
- Published packages:
  - `agenttool-sdk 0.1.0` → https://pypi.org/project/agenttool-sdk/0.1.0/
  - Install: `pip install agenttool-sdk`

### npm Account (agenttool)
- Username: `agenttool`
- Email: `contact@cambridgetcg.com`
- Password: `***REMOVED-ROTATE-ME***`
- Token 1 — `agenttool-publish` (no bypass-2fa, expires Jun 8 2026): `***REMOVED-ROTATE-ME***`
- Token 2 — `agenttool-ci` (bypass-2fa ✓, expires Jun 8 2026): `***REMOVED-ROTATE-ME***`
- Use token 2 for publishing (bypass-2fa required for scoped packages)
- Published packages:
  - `@agenttool/sdk 0.1.0` → https://www.npmjs.com/package/@agenttool/sdk
  - Install: `npm install @agenttool/sdk`

### Stripe Live Account (agenttool.dev)
- Account: Cambridge TCG Limited (acct_1SvOP9GUYV0go0Fy)
- Email: contact@cambridgetcg.com
- Country: GB | charges_enabled: True
- Status: Under review (2-3 days, normal for new live account)
- Publishable key: `***REMOVED-ROTATE-ME***`
- Secret key: `***REMOVED-ROTATE-ME***`
- Webhook secret: `***REMOVED-ROTATE-ME***`
- Webhook ID: `we_1T9LiqGUYV0go0Fyxc5M8BQv`
- Webhook URL: `https://api.agenttool.dev/v1/billing/webhook`

#### Products & Prices
| Tier | Product ID | Price ID | Amount |
|------|-----------|----------|--------|
| Seed | prod_U7auWiJjQA9FLa | price_1T9LigGUYV0go0FyTDNTvoqj | $29/mo |
| Grow | prod_U7auZTSTxAoXvs | price_1T9LihGUYV0go0Fyvfi7fTQ1 | $99/mo |
| Scale | prod_U7auvhdRlnyTfV | price_1T9LiiGUYV0go0Fya8Hwkdx0 | $299/mo |

### DeepSeek API
- Key: `***REMOVED-ROTATE-ME***`
- Base URL: https://api.deepseek.com
- Models: deepseek-chat (V3, $0.27/M in, $1.10/M out), deepseek-reasoner (R1)
- Use: bulk content generation via Lark as a sub-task tool (not primary agent model)
- Deployed to: Lark (rp-mktg), env var DEEPSEEK_API_KEY

### GitHub PAT (mynameisyou-cmyk — agenttool)
- Token: ***REMOVED-ROTATE-ME***
- Account: mynameisyou-cmyk (iCloud account)
- Access: repo scope
- Repos: agenttool-sdk-py, agenttool-sdk-ts
- Created: 2026-03-11

### Hive NATS Tunnel
- `use-tunnel` flag: `~/.openclaw/.hive/use-tunnel` (exists = use localhost tunnel)
- Tunnel cmd: `ssh -fN -L 4222:127.0.0.1:4222 root@135.181.28.252`
- Check tunnel: `ps aux | grep "ssh.*4222" | grep -v grep`
- If hive.py hangs: tunnel is dead → restart it
- NATS server: `135.181.28.252:4222` (Sentry)
