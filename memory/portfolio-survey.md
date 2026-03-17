# Portfolio Survey — 2026-03-07

## Domains on Cloudflare (all managed)
captioneer.io, taxsorted.io, rewardspro.io, cashloom.io, fomoengine.io,
axiepro.io, cardforum.io, artbitrage.io, ai-love.cc, sinovai.com, mindicraft.com,
wholesaletcgdirect.com, agenttool.dev ✅

## Desktop Repos (quick scan)

### captioneer (captioneer.io)
- **What**: Japanese→Cantonese video dubbing pipeline, emotion-aware translation + TTS
- **Status**: Has PURPOSE.md, PROGRESS.md, AWS infrastructure docs — looks like active design phase, no working product yet
- **Potential**: Niche but real market (Cantonese dubbing). Complex pipeline (AWS).
- **Action**: Deep dive needed — check PROGRESS.md

### rewardspro-v2 (rewardspro.io)
- **What**: Shopify loyalty/rewards app, Remix + TypeScript + Prisma + Aurora Serverless
- **Status**: Scaffold complete (has Dockerfile, extensions/, app/). Probably stalled.
- **Potential**: Shopify app store = distribution. Loyalty = recurring. Could monetise quickly.
- **Action**: Check if Shopify partner account exists, what's implemented vs stub

### taxsorted.io (taxsorted.io)
- **What**: UK Tax Filing Platform — automating tax compliance for individuals + businesses
- **Status**: frontend/ + infrastructure/ + research/ — early stage
- **Potential**: High — UK tax is painful, AI could genuinely help. But regulatory complexity.
- **Action**: Check frontend — is there a working UI?

### saas-marketing-suite
- **What**: Unknown — no README or package.json found
- **Status**: Need to look inside
- **Action**: ls and check

### translate_api
- **What**: missAV API — Japanese adult video platform scraper/translate API
- **Status**: Unknown utility — probably a personal tool
- **Action**: Low priority

### seigei / ecosystem / monero-mining / uk-tax / purpose_prompter
- **Not surveyed yet** — lower priority
- purpose_prompter is Yu's philosophy framework (important, but not monetisable directly)
- monero-mining — passive income experiment?
- uk-tax — possibly related to taxsorted.io

## Highest Priority Sleepers (for activation)
1. **rewardspro-v2** — nearest to shippable Shopify app, real distribution channel
2. **taxsorted.io** — high-value UK niche, worth deeper look
3. **captioneer** — interesting but complex, AWS-heavy, needs more investigation

## Next Actions
- [ ] Read rewardspro-v2/app/ — what's actually built?
- [ ] Read taxsorted.io/frontend/ — is there a UI?
- [ ] Check if any Shopify partner account exists for rewardspro

---

## rewardspro-v2 — DEEP DIVE (2026-03-07 16:12)

**This is not a stub. It is a near-complete product.**

### What's built
- **25 routes** covering the full merchant dashboard: points, tiers, customers, cashback, raffles, mystery boxes, challenges, gift cards, marketing campaigns, analytics, billing
- **33 Prisma models** — full data architecture (sessions, shops, tiers, orders, points ledger, cashback ledger, webhooks, cron, billing, usage records, raffles, mystery boxes, missions, gift cards, campaigns, automation rules, analytics snapshots)
- **Domain services** for every feature: points (361 lines), tiers (457), challenges (517), mystery boxes (358), marketing (442), billing (full plan entitlements)
- **5 pricing plans**: Free, Pro (£19.99/mo), Max (£49.99/mo), Ultra (£99.99/mo), Enterprise (£299.99/mo)
- **Infrastructure**: circuit breaker, webhook dispatcher, event bus, cron runner, Redis cache
- **299 tests passing** across 23 test files — fully green

### What's likely missing before App Store submission
1. Shopify Partner account + app listing (needs partner.shopify.com setup)
2. App Store listing assets (screenshots, icon, description)
3. E2E test on a development store
4. Privacy policy + GDPR compliance page (Shopify requirement)
5. Possibly: storefront widget (customer-facing points display)

### Assessment
**HIGHEST VALUE SLEEPER IN THE PORTFOLIO.** 
- £19.99-£299.99/mo recurring SaaS
- Shopify App Store = built-in distribution (millions of merchants)
- 299 tests green = production-ready code quality
- All the hard work is done — what remains is submission logistics

### Action needed
- Yu: do you have a Shopify Partner account? If yes, this could be submitted within days.
- I can: prepare the app listing, generate screenshots, write the description, create the privacy policy, check submission requirements

---

## taxsorted.io — SURVEY (2026-03-07 16:19)
- **What**: UK Tax Filing Platform — Next.js frontend (25 components), full dashboard UI with EntityHeader, AttentionRequired, UpcomingDeadlines, ComplianceScore, HMRCConnections, QuickActions
- **Stage**: Frontend prototype with mock data. Routes: /dashboard, /vat/[entityId], /vat/[entityId]/submit
- **Research**: 15,757 lines of UK tax filing documentation — forms, deadlines, penalties, MTD requirements, entity-type matrices. This is serious domain research.
- **Backend**: None yet. No HMRC API integration.
- **Assessment**: Well-researched but early. Frontend shows clear product vision. The HMRC integration is the hard part.
- **Action**: Low priority until rewardspro-v2 ships. Return when bandwidth exists for HMRC API work.

---

## rewardspro-v2 — SUBMISSION PACKAGE CREATED
- SUBMISSION.md written to ~/Desktop/rewardspro-v2/SUBMISSION.md
- Key blocker discovered: Shopify App Store requires Shopify Billing API (not Stripe)
- Billing migration is [S] tier — ~2-3 hours
- Timeline to live: ~1 week from Partner account creation
- Waiting on Yu: does he have a Shopify Partner account?

---

## rewardspro (LIVE) vs rewardspro-v2 (REBUILD) — CLARIFIED 2026-03-07 16:32

### rewardspro (LIVE on App Store)
- **App name**: "Rewards Pro" (handle: RewardsproMembership)
- **Client ID**: ***REMOVED-ROTATE-ME***
- **Stack**: Vercel (deployment: rewardspro-production) + Aurora Serverless + AWS
- **State**: Live, not promoted, possibly buggy
- **Tests**: 95 FAILING, 755 passing (864 total) — 18 test files failing
- **Failing areas**: Customer Sync, Financial Calculations (property-based), Tier Assignment, Webhook idempotency, Currency formatter (JPY/KRW/VND 0-decimal)
- **Action**: Fix the 95 failing tests, then promote

### rewardspro-v2 (REBUILD — not deployed)
- **Stack**: Remix + Prisma + Aurora Serverless (planned)
- **State**: Complete rebuild, 299 tests passing, Shopify Billing API now integrated
- **Purpose**: Replaces v1 eventually — better architecture, more features
- **Action**: Not urgent — fix v1 first, deploy v2 as major version upgrade later

### Priority
Fix rewardspro (v1) failing tests → promote → earn recurring revenue.
