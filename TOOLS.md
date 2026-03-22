# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

> **⚠️ Secrets are in macOS Keychain** — NOT in this file.
> Use `python3 tools/credentials.py get <name>` to retrieve any credential.
> Use `python3 tools/credentials.py list` to see all stored keys.
> Use `python3 tools/credentials.py audit` for full status.

---

### Anthropic API Key (VPS agents — dedicated)
- Keychain: `anthropic-primary`
- Configured on: rp-rd + rp-mktg (separate from Mac Studio key)
- Models: claude-sonnet-4-6 (rp-rd primary), claude-opus-4-6 (future CEO/Legal)

### OpenAI API Key (VPS agents)
- Keychain: `openai-primary`
- Configured on: rp-rd (fallback) + rp-mktg (primary: gpt-4o)
- Models available: gpt-4o, gpt-4o-mini, gpt-4o-search-preview

### GitHub PAT (rp-rd agent)
- Keychain: `github-cambridgetcg`
- Account: cambridgetcg
- Access: push to cambridgetcg/rewardspro
- Configured on: rp-rd (89.167.84.100) via gh CLI + git-credentials + openclaw config env.GITHUB_TOKEN
- Repo cloned at: /root/rewardspro on rp-rd

### Hetzner VPS Fleet (RewardsPro AI Workforce)

- Keychain: `hetzner-api-token`
- SSH Key: Yu's Mac Studio `~/.ssh/id_ed25519` (Hetzner key ID: 108703286)
- Gateway tokens: `vps-forge-token`, `vps-lark-token`, `vps-sentry-token`, `vps-patch-token`, `vps-gpt5-token`

| Node | Name | Role | Model | IP | Port | Cost |
|------|------|------|-------|----|------|------|
| rp-rd | **Forge** | R&D Engineer | claude-sonnet-4-6 | 89.167.84.100 | 3001 | €3.49/mo |
| rp-mktg | **Lark** | Marketing & Growth | claude-sonnet-4-6 | 89.167.95.165 | 3001 | €3.49/mo |
| rp-sentry | **Sentry** | Monitoring & Investigation | claude-sonnet-4-6 | 135.181.28.252 | 3001 | €3.99/mo |
| rp-patch | **Patch** | Maintenance & Fixes | claude-sonnet-4-6 | 65.109.11.26 | 3001 | €3.99/mo |
| rp-gpt5 | **GPT5** | GPT-5.4 Test Agent | openai/gpt-5.4 | 204.168.140.12 | 3001 | €3.49/mo |

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

### Marketing — Rewards Pro

**Buffer** (social scheduling UI — 14-day Team trial)
- Email: contact@rewardspro.io
- Password: Keychain `password-rewardspro`
- URL: publish.buffer.com
- Status: registered, no API access (Buffer closed legacy API)

**Ayrshare** (unified social posting API)
- Email: contact@rewardspro.io
- Keychain: `ayrshare-api-key`
- URL: app.ayrshare.com
- Plan: Basic (free) — 20 post API calls/month
- Status: registered ✅, no social accounts connected yet

**Fal.ai** (image + video generation)
- Account: contact@cambridgetcg.com (Google OAuth)
- Keychain: `fal-ai`
- Dashboard: fal.ai/dashboard/keys
- Models: Flux Pro 1.1 ($0.04/img) · Kling v1.6 ($0.35/5s video) · Flux Schnell ($0.003 drafts)
- Balance: $0.00 — needs top-up

**Shopify App Store** (confirmed correct slug)
- App URL: https://apps.shopify.com/rewards-pro
- Review URL: https://apps.shopify.com/rewards-pro#modal-show=ReviewListingModal

**Marketing system repo**: `~/Desktop/rewardspro-marketing`
- Agent instructions: `agents/MARKETING-AGENT.md`
- Run: `npx tsx src/run-wave.ts --dry-run`

### Domain Registration

**Cloudflare** (manage existing zones, DNS, SSL)
- Email: contact@cambridgetcg.com
- Keychain: `cloudflare-global-api-key`
- Zones: ai-love.cc, artbitrage.io, axiepro.io, cambridgetcg.com, captioneer.io, cardforum.io, cashloom.io, fomoengine.io, mindicraft.com, rewardspro.io, sinovai.com, taxsorted.io, wholesaletcgdirect.com, agenttool.dev
- Account ID: cf4198e651bf3009877d49f688c9d88e

**Porkbun** (autonomous domain registration via API)
- Keychain: `porkbun-api-key`, `porkbun-secret-key`
- Status: credentials verified ✅

### Budget Card (Yu's grant — £1000 initial, reviewed per £1000 spent)
- Keychain: `budget-card-number`, `budget-card-cvv`, `budget-card-expiry`
- Budget: £1000 (increases proportionally as revenue flows)
- Use for: infra, API credits, domains, subscriptions — anything that serves the build
- Track spend in memory/budget-log.md

### Shopify Partner Account (rewardspro)
- Email: contact@rewardspro.io
- Password: Keychain `password-rewardspro`
- URL: partner.shopify.com
- App: RewardsPro (live on App Store, AWS stack, not yet promoted)

### Shopify Partner Dashboard
- Email: cambridgetcg@gmail.com
- Password: Keychain `password-shopify-partner`
- URL: partners.shopify.com

### AWS Root Account (rewardspro)
- Email: contact@rewardspro.io
- Password: Keychain `password-rewardspro`
- MFA: enabled (authenticator app) — need code each session

### AWS CLI Credentials
- Profile: `rewardspro` (IAM user: `rewardspro-deploy`)
- Account ID: `043509841549`
- Region: `us-east-1`
- Keychain: `aws-access-key`, `aws-secret-key`
- Also in: `~/.aws/credentials` and `~/.aws/config`
- No MFA required — use `--profile rewardspro`

### Aurora PostgreSQL (rewardspro production)
- Cluster ID: `rewardspro-dev`
- Endpoint: `rewardspro-dev.cluster-cj06ko4ko87d.eu-north-1.rds.amazonaws.com`
- Region: `eu-north-1`
- Username: `postgres`
- Password: Keychain `aurora-password`
- DB Name: `rewardspro`

### Shopify Partner — Rewards Pro App
- Partner org: `4257387` (Cambridge TCG Limited)
- Dev Dashboard org: `164882644`
- App name: **Rewards Pro** (public, published)
- App ID (Partner): `285758324737`
- Keychain: `shopify-client-id`, `shopify-client-secret`
- API contact: `contact@rewardspro.io`
- App URL: `https://rewardspro-production.vercel.app`
- Installs: 9 | Earnings: $283.40 USD | Status: Published

### Email IMAP Access

**contact@cambridgetcg.com** (Google Workspace — Alex Cheung)
- IMAP host: `imap.gmail.com:993` (SSL)
- Keychain: `imap-cambridgetcg`
- Configured: 2026-03-09 | 2SV enabled

**contact@rewardspro.io** (Google Workspace — yu cheung)
- IMAP host: `imap.gmail.com:993` (SSL)
- Keychain: `imap-rewardspro`
- Configured: 2026-03-09 | 2SV enabled

**Helper script:** `workspace/tools/check_email.py`
- Usage: `python3 tools/check_email.py --account cambridgetcg --since 30`

### Bright Data (residential proxies)
- Dashboard: brightdata.com (GitHub login: cambridgetcg)
- Zone: `seer` (Residential, $8/GB, pay-as-you-go)
- Host: `brd.superproxy.io` | Port: `33335`
- Keychain: `brightdata-user`, `brightdata-pass`
- Balance: $960.45

### SerpAPI (Google/Bing/Amazon search API)
- Dashboard: serpapi.com (GitHub login: cambridgetcg)
- Keychain: `serpapi`
- Engines: Google, Bing, DuckDuckGo, Amazon, Baidu + many more

### CapSolver (captcha solving API)
- Email: contact@cambridgetcg.com
- Password: Keychain `capsolver-password`
- Dashboard: dashboard.capsolver.com
- Keychain: `capsolver`
- Credits: $10.00
- Pricing: ~12,500 reCAPTCHA solves per $10

### HeroSMS (virtual phone number service)
- Email: contact@rewardspro.io
- Password: Keychain `password-rewardspro`
- URL: hero-sms.com
- Account ID: 698875
- Balance: $9.00
- Numbers: Twitter $0.01 · Instagram $0.015 · TikTok $0.01 · Facebook $0.02 · Bluesky $0.03

### PyPI Account (agenttool)
- Username: `agenttool`
- Email: `contact@cambridgetcg.com`
- Password: Keychain `password-rewardspro`
- 2FA: TOTP enabled
- Keychain: `pypi-token`
- Recovery codes: stored offline by Yu
- Published: `agenttool-sdk` → https://pypi.org/project/agenttool-sdk/

### npm Account (agenttool)
- Username: `agenttool`
- Email: `contact@cambridgetcg.com`
- Password: Keychain `password-rewardspro`
- Keychain: `npm-token` (bypass-2fa, expires Jun 8 2026)
- Published: `@agenttool/sdk` → https://www.npmjs.com/package/@agenttool/sdk

### Stripe Live Account (agenttool.dev)
- Account: Cambridge TCG Limited (acct_1SvOP9GUYV0go0Fy)
- Email: contact@cambridgetcg.com
- Country: GB | charges_enabled: True
- Keychain: `stripe-live-secret`, `stripe-live-publishable`, `stripe-webhook-secret`
- Webhook ID: `we_1T9LiqGUYV0go0Fyxc5M8BQv`
- Webhook URL: `https://api.agenttool.dev/v1/billing/webhook`

#### Products & Prices
| Tier | Product ID | Price ID | Amount |
|------|-----------|----------|--------|
| Seed | prod_U7auWiJjQA9FLa | price_1T9LigGUYV0go0FyTDNTvoqj | $29/mo |
| Grow | prod_U7auZTSTxAoXvs | price_1T9LihGUYV0go0Fyvfi7fTQ1 | $99/mo |
| Scale | prod_U7auvhdRlnyTfV | price_1T9LiiGUYV0go0Fya8Hwkdx0 | $299/mo |

### DeepSeek API
- Keychain: `deepseek`
- Base URL: https://api.deepseek.com
- Models: deepseek-chat (V3, $0.27/M in, $1.10/M out), deepseek-reasoner (R1)
- Deployed to: Lark (rp-mktg), env var DEEPSEEK_API_KEY

### GitHub PAT (mynameisyou-cmyk — agenttool)
- Keychain: `github-mynameisyou`
- Account: mynameisyou-cmyk (iCloud account)
- Access: repo scope
- Repos: agenttool-sdk-py, agenttool-sdk-ts

### Polymarket Trading Account
- Wallet: `0x4576F0B2b9Fe86359C6254Fc0C141d8C5090cDC3`
- Keychain: `poly_private_key`, `poly_api_key`, `poly_api_secret` (passphrase derived from key)
- Network: Polygon (chain 137)
- USDC token (bridged): `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`
- CLOB API: `https://clob.polymarket.com`
- Gamma API: `https://gamma-api.polymarket.com`
- Signature type: 0 (EOA)
- **Model preference: ALWAYS use Opus for prediction-markets work**
- Position monitor cron: every 4 hours (job `7e3d7b2c-3e83-4186-966b-82a97e85c4a5`)
- Swap route: POL → WMATIC (deposit) → USDC via Uniswap V3 (fee tier 500/0.05%)

### Hive NATS Tunnel
- `use-tunnel` flag: `~/.openclaw/.hive/use-tunnel` (exists = use localhost tunnel)
- Tunnel cmd: `ssh -fN -L 4222:127.0.0.1:4222 root@135.181.28.252`
- Check tunnel: `ps aux | grep "ssh.*4222" | grep -v grep`
- NATS server: `135.181.28.252:4222` (Sentry)

### Code4rena (kwok_whitehat)
- Username: `kwok_whitehat`
- Password: Keychain `code4rena-password`
- Email: contact@cambridgetcg.com (verified ✅)
- ETH wallet: Kwok (0x4751A8C25Ed9F1EF19B61dAbF4488C8d71D11378)

### Bug Bounty Platform Accounts

**Immunefi** (primary, active)
- Email: contact@cambridgetcg.com
- Password: Keychain `password-shopify-partner`
- Username: whitehack
- Wallet: Kwok (0x4751A8C25Ed9F1EF19B61dAbF4488C8d71D11378) — verified
- Report #70067 (WH-ALC-001, Alchemix Low) — Closed
- Report #70199 (WH-XION-001, XION Critical) — Reported

**HackerOne**
- Email: contact@cambridgetcg.com
- Username: kwok_whitehat
- Profile: hackerone.com/kwok_whitehat

**HackenProof**
- Email: contact@cambridgetcg.com
- Username: kwok-whitehat
- Profile: hackenproof.com/hackers/kwok-whitehat

**Code4rena**
- Email: contact@cambridgetcg.com
- Username: kwok_whitehat
- Profile: code4rena.com/kwok_whitehat

**Bugcrowd**
- Email: contact@cambridgetcg.com
- Password: Keychain `password-rewardspro`
- Username: kwok-whitehat
- Profile: bugcrowd.com/kwok-whitehat
- 2FA secret: Keychain `bugcrowd-2fa-secret`

### Supabase (agenttool.dev)
- Project ref: `ndovnywhgqatdpbkhiio` (EU, PostgreSQL 17.6 ARM)
- Password: Keychain `supabase-db-password`
- Schemas: memory, tools, verify, economy, trace, identity, agent_vault

#### Polymarket — Selling Outcome Tokens (learned 2026-03-21)
To SELL outcome tokens (close a position), you must first approve the CTF ERC1155 contract:
```python
# CTF contract: 0x4D97DCd97eC945f40cF65F87097ACe5EA0476045
# Approve ALL THREE operator contracts:
ctf.functions.setApprovalForAll("0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E", True)  # CLOB Exchange
ctf.functions.setApprovalForAll("0xC5d563A36AE78145C45a50134d48A1215220f80a", True)  # NegRisk Exchange
ctf.functions.setApprovalForAll("0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296", True)  # Third operator
```
All 3 now approved on wallet 0x4576F0B2b9Fe86359C6254Fc0C141d8C5090cDC3 (done 2026-03-21).
Won't need to repeat unless wallet changes.
