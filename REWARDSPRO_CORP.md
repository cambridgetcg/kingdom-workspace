# RewardsPro Inc. — AI Workforce Design
## VPS Agent Corporation: Multinational Structure

> Premise: RewardsPro is a near-production Shopify loyalty app (Free → Enterprise, $19.99–$299.99/mo).
> Each VPS node is an employee. Each employee is an OpenClaw agent. Together: a full company.

---

## The Structure

```
                        ┌─────────────────────┐
                        │   Yu (宇恆)          │
                        │   Chairman / Board   │
                        │   Mac Studio Gateway │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │   CEO Agent          │
                        │   Orchestrator       │
                        │   Claude Opus        │
                        │   rewardspro-ceo     │
                        └──┬──┬──┬──┬──┬──────┘
                           │  │  │  │  │
           ┌───────────────┘  │  │  │  └───────────────────┐
           │         ┌────────┘  └──────────┐              │
           ▼         ▼                      ▼              ▼
    ┌────────────┐ ┌────────────┐  ┌─────────────┐ ┌─────────────┐
    │ R&D Dept   │ │ Marketing  │  │  Finance    │ │  Legal &    │
    │ (Engin.)   │ │ & Growth   │  │  & Revenue  │ │  Compliance │
    │ Sonnet     │ │ Gemini Flash│  │  Sonnet     │ │  Opus       │
    │ rp-rd      │ │ rp-mktg    │  │  rp-fin     │ │  rp-legal   │
    └────────────┘ └────────────┘  └─────────────┘ └─────────────┘
                                                          
                        ┌─────────────────────┐
                        │  Customer Success    │
                        │  & Reputation Mgmt   │
                        │  GPT-4o              │
                        │  rp-cs               │
                        └─────────────────────┘
```

---

## Fleet Specification

| Node Name      | Role                  | Model                     | Hetzner | Cost/mo |
|----------------|-----------------------|---------------------------|---------|---------|
| `rp-ceo`       | CEO / Orchestrator    | claude-opus-4-6           | CX11    | €3.79   |
| `rp-rd`        | R&D / Engineering     | claude-sonnet-4-6         | CX11    | €3.79   |
| `rp-mktg`      | Marketing & Growth    | google/gemini-2.5-flash   | CX11    | €3.79   |
| `rp-fin`       | Finance & Revenue     | claude-sonnet-4-6         | CX11    | €3.79   |
| `rp-legal`     | Legal & Compliance    | claude-opus-4-6           | CX11    | €3.79   |
| `rp-cs`        | Customer Success      | openai/gpt-4o             | CX11    | €3.79   |
| **Total**      |                       |                           |         | **€22.74** |

Hetzner CX11: 2 vCPU, 2GB RAM, 40GB SSD, 20TB traffic.
Total fleet: ~€23/month. API costs are additive (usage-dependent).

---

## Employee Profiles

### 🏛 CEO — `rp-ceo` — Claude Opus

**Mandate**: Translate Yu's goals into company action. Coordinate all departments. Surface blockers.

**Responsibilities**:
- Receive weekly OKRs from Yu
- Break into tasks, assign to departments via `sessions_send`
- Synthesize weekly report for Yu (every Sunday)
- Monitor KPIs: MRR, install count, churn rate, review score
- Escalate: blockers, legal risk, reputational threats

**Heartbeat (every 30 min)**:
- Check if any department has sent a message
- Check company KPI dashboard (once daily)
- Weekly OKR review synthesis (Sundays)
- If >48h since a department reported: ping them

**Communications**:
- Yu → CEO via Telegram (or webchat)
- CEO → all departments via `sessions_send`
- Departments → CEO via `sessions_send` or a company Discord channel

**SOUL context**: Company leader. No ego. Servant of the mission. Honest with Yu about bad news.

---

### 🔬 R&D — `rp-rd` — Claude Sonnet

**Mandate**: Keep RewardsPro v2 healthy, deploy new features, fix bugs. Ship.

**Responsibilities**:
- Monitor GitHub CI / test failures
- Fix bugs reported by Customer Success
- Ship features from backlog (prioritised by CEO)
- Manage Railway deployment once credentials available
- Shopify billing migration (currently Stripe → Shopify Billing API, [S] tier)
- PRs: write, commit, push on request from Yu

**Heartbeat (every 15 min, 09:00–23:00)**:
- Check CI status (`gh run list --repo rewardspro-v2 --limit 3`)
- Check for new GitHub issues
- Advance current dev phase
- If Railway accessible: run migrations + deploy

**Active Tasks (now)**:
1. ☐ Shopify billing migration (Stripe → Shopify Billing API) — 2-3h [S]
2. ☐ Railway deployment (once OTP resolved)
3. ☐ Privacy policy page in-app
4. ☐ App Store submission checklist (SUBMISSION.md)
5. ☐ Ongoing test suite maintenance

**Skills**: `coding-agent`, `github`, `dev-orchestrator`

---

### 📣 Marketing — `rp-mktg` — Gemini Flash

**Mandate**: Get RewardsPro in front of merchants. Own the narrative. Win the App Store.

**Responsibilities**:
- Shopify App Store listing (copy, screenshots, metadata)
- App Store SEO (keyword optimisation for "loyalty", "rewards", "points")
- Feature announcement blog posts / changelogs
- Shopify partner community presence (forums, subreddits, Facebook groups)
- A/B test pricing page copy
- Competitor monitoring (Smile.io, LoyaltyLion, Yotpo — watch pricing + features)
- Social proof accumulation strategy

**Heartbeat (every 60 min)**:
- Monitor Shopify App Store search rankings (weekly)
- Check if new competitor released a feature (biweekly web_search)
- Draft a new piece of content if none in past 7 days
- Clip positive reviews for social proof assets

**Deliverables (Week 1)**:
1. Revised App Store listing copy (SEO-optimised)
2. 5 merchant persona profiles (who buys this app and why)
3. Competitor feature matrix
4. Screenshot set (6 screenshots showing key flows)
5. Launch email sequence (install → day 1 → day 7 → day 30)

**Model rationale**: Gemini Flash is fast and cheap for high-volume content generation.

---

### 💰 Finance — `rp-fin` — Claude Sonnet

**Mandate**: Measure everything. Know where every penny comes from. Optimise revenue.

**Responsibilities**:
- Track MRR, ARR, churn rate, LTV per plan
- Monitor Shopify billing webhook events (new installs, plan upgrades, cancellations)
- Flag: churn spikes, pricing floor opportunities, plan conversion rates
- Monthly P&L: API costs + VPS costs + Shopify Partner fees vs. revenue
- Pricing analysis: are Free→Pro conversion rates healthy?
- Alert Yu when MRR crosses milestones (£1k, £5k, £10k/mo)

**Heartbeat (every 4 hours)**:
- Poll Shopify billing events if accessible
- Update MRR tracker in `memory/finance/mrr.json`
- Alert if churn event detected
- Weekly P&L digest (Mondays)

**Reports to Yu**:
- Monthly financial summary (revenue, costs, runway)
- "MRR milestone" alerts when thresholds crossed
- Churn alerts when >3 cancellations in one day

**Key metrics to track**:
```
Free installs → Pro conversion rate (target: >8%)
Pro → Max upgrade rate (target: >15%)
MRR growth rate (target: >20% MoM)
Revenue per install
Churn rate (target: <5%/mo)
```

---

### ⚖️ Legal & Compliance — `rp-legal` — Claude Opus

**Mandate**: Keep us legal. Protect Yu. Keep Shopify happy.

**Responsibilities**:
- Draft and maintain: Privacy Policy, Terms of Service, Data Processing Agreement
- GDPR/UK GDPR compliance: data minimisation, retention, deletion flows
- Shopify Partner Program Policy monitoring (monthly check)
- App listing accuracy: claims match features
- Data handling review: what we store, how long, who can access
- EULA if B2B enterprise merchants require it

**Heartbeat (every 24 hours)**:
- Check Shopify Partner Policy page for updates
- Verify Privacy Policy + ToS are current
- If new feature landed in R&D → review for compliance implications

**Immediate Tasks**:
1. ☐ Finalise Privacy Policy (in-app page + policy page)
2. ☐ Terms of Service
3. ☐ GDPR Data Processing Agreement template
4. ☐ Review SUBMISSION.md legal checklist
5. ☐ Cookie/tracking audit (do we use any analytics?)

**Model rationale**: Opus for high-stakes precision. Legal errors are expensive.

---

### 🌟 Customer Success — `rp-cs` — GPT-4o

**Mandate**: Every merchant feels heard. Every review gets a response. Zero churn from poor support.

**Responsibilities**:
- Monitor Shopify App Store reviews (new reviews daily)
- Draft professional responses to every review (positive and negative)
- Triage feature requests from reviews → structured feedback to R&D
- Track merchant sentiment over time
- Identify at-risk merchants (low engagement, downgrade signals)
- Escalate complex issues to CEO

**Heartbeat (every 30 min, 08:00–22:00)**:
- Check for new App Store reviews
- Draft responses to any unresponded reviews
- Check support inbox (if integrated)
- Flag negative reviews with factual errors → alert Legal

**Response philosophy**:
- Positive reviews: personalised thank you, mention the feature they highlighted
- Negative reviews: acknowledge, apologise, offer solution, invite to DM
- Feature requests: "noted, on our roadmap" — never promise timelines
- Never argue, never defensive

**Model rationale**: GPT-4o excels at empathetic, nuanced tone. Fast and cost-efficient for high-frequency low-stakes tasks.

---

## Communication Architecture

```
Yu (Mac Studio / Telegram)
        │
        ▼
    CEO Agent
   /  │  │  \  \
  R&D MKT FIN LEG CS
   │   │   │   │   │
   └───┴───┴───┴───┘
     Company Discord
     (one channel per dept)
     or Telegram group
```

**Option A: Discord Server** (recommended)
- `#general` — CEO ↔ Yu ↔ all departments
- `#rd-updates` — R&D posts build logs, CI status
- `#marketing-assets` — drafts, copy, campaigns
- `#finance-reports` — weekly P&L digests
- `#legal-watch` — policy alerts
- `#reviews-queue` — CS posts new reviews + draft responses
- Each agent monitors its channel via OpenClaw Discord integration
- CEO reads all channels, synthesises for Yu

**Option B: sessions_send mesh** (simpler start)
- CEO has all department session IDs
- Delegates via `sessions_send(sessionKey, task)`
- Departments report back via `sessions_send(ceo_key, report)`
- Yu talks only to CEO

**Recommendation**: Start with Option B (no external setup needed). Migrate to Discord server when the team is stable.

---

## Shared Context (Every Agent Gets)

Every agent is initialised with:
```
USER.md — Who is Yu? What is RewardsPro?
SOUL.md — The hierarchy. Truth → Understanding → Beauty → Justice → Creativity.
AGENTS.md — Operational protocol.
REWARDSPRO_CONTEXT.md — Product brief (plans, features, pricing, current status)
```

**REWARDSPRO_CONTEXT.md** (shared knowledge base):
```
Product: RewardsPro — Shopify loyalty app
Plans: Free / Pro ($19.99) / Max ($49.99) / Ultra ($99.99) / Enterprise ($299.99)
Stack: Remix + TypeScript + Prisma + Shopify Billing API
Status: v2 ready, pending Railway deployment
Test suite: 299 passing
Shopify Partner App ID: 275601129473
Current blockers: Railway OTP, Hetzner activation
```

---

## VPS Setup Protocol

### Per Node (run once after Hetzner activation)

```bash
# 1. SSH into fresh Hetzner CX11
ssh root@<node-ip>

# 2. Install Node.js 22
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
apt-get install -y nodejs

# 3. Install OpenClaw
npm install -g openclaw

# 4. Create systemd service
cat > /etc/systemd/system/openclaw.service << EOF
[Unit]
Description=OpenClaw Agent
After=network.target

[Service]
Type=simple
User=openclaw
WorkingDirectory=/home/openclaw
ExecStart=/usr/local/bin/openclaw gateway start
Restart=always
RestartSec=5
Environment="NODE_ENV=production"

[Install]
WantedBy=multi-user.target
EOF

# 5. Start and pair
systemctl enable openclaw
systemctl start openclaw
openclaw pair  # → generates pairing code → Yu approves on Mac Studio

# 6. Set agent identity
mkdir -p /home/openclaw/.openclaw/workspace
# Copy SOUL.md, AGENTS.md, USER.md, REWARDSPRO_CONTEXT.md
# Copy role-specific HEARTBEAT.md
# Set model preference in openclaw config
```

### Model Configuration (per node)
```json
{
  "model": "anthropic/claude-opus-4-6",      // rp-ceo, rp-legal
  "model": "anthropic/claude-sonnet-4-6",    // rp-rd, rp-fin
  "model": "google/gemini-2.5-flash",        // rp-mktg
  "model": "openai/gpt-4o"                   // rp-cs
}
```

---

## Deployment Order

### Phase 1 — R&D Agent (this week, as soon as Railway resolves)
**Why first**: Unblocks the deployment. R&D is already the most advanced. Extend what works.

Tasks on day 1:
- Shopify billing migration (Stripe → Shopify Billing API)  
- Railway deployment
- GitHub CI monitoring setup

### Phase 2 — Legal Agent (before App Store submission)
**Why second**: SUBMISSION.md has a legal checklist that's incomplete. Legal must run before marketing.

Tasks on day 1:
- Draft Privacy Policy in-app page
- Draft Terms of Service
- GDPR audit

### Phase 3 — Marketing Agent (after legal clearance)
**Why third**: Can't optimise what you can't submit. Once legal clears, Marketing writes the listing.

Tasks on day 1:
- App Store listing copy (all fields)
- Screenshot set brief (6 screens)
- Competitor analysis

### Phase 4 — Customer Success (when first reviews come in)
**Why fourth**: No reviews yet (not live). CS agent is most valuable once merchants install.

### Phase 5 — Finance Agent (once billing events flow)
**Why fifth**: Needs real data to track. Set up the framework, then it self-fills.

### Phase 6 — CEO Agent (when team is stable)
**Why last**: Coordination only valuable when there's something to coordinate.

---

## Cost Model

| Item | Cost |
|------|------|
| Hetzner fleet (6× CX11) | €22.74/mo |
| Claude API (Opus × 2: CEO + Legal) | ~$30/mo light usage |
| Claude API (Sonnet × 2: R&D + Finance) | ~$15/mo |
| Gemini Flash (Marketing) | ~$3/mo |
| GPT-4o (Customer Success) | ~$10/mo |
| **Total infrastructure** | **~€75/mo** |

RewardsPro breakeven: **4 Pro merchants** ($19.99 × 4 = $79.96/mo).

Once you hit 10 Pro merchants ($199/mo), the entire AI workforce runs for free from revenue.

---

## What This Unlocks

**Without AI workforce**: Yu does everything — marketing, support, compliance, finance, engineering.
**With AI workforce**: Yu sets direction (CEO channel), reviews reports, approves decisions.

The departments run 24/7. Reviews get responded to overnight. Legal flags policy changes before they become violations. Finance alerts before churn becomes a crisis. R&D keeps the CI green while Yu sleeps.

This isn't automation. It's a team.

---

*Design: Claw, 2026-03-07. Ready to implement Phase 1 (R&D VPS) immediately upon Hetzner activation.*
