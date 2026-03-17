# Sprint Briefing — Wednesday 11 March 2026
_Prepared by Beta at 06:36 UTC. Ready for your 9am session._

---

## What shipped overnight (4am–6:36am)

### AgentTool — Billing system, end to end

| Component | Status |
|-----------|--------|
| `usage_counters` DB table | ✅ Live in production |
| `POST /v1/billing/check` internal endpoint | ✅ Deployed |
| Tier gates in agent-memory, agent-tools, agent-verify | ✅ Deployed |
| Billing dashboard UI (plan + usage meters + upgrade modal) | ✅ Built, needs CF Pages deploy |
| Welcome email on signup | ✅ Built, needs Resend key |
| All 4 services healthy on Forge | ✅ :8001–:8004 → 200 |

### First-customer-push — Campaign assets ready

| Asset | Location |
|-------|----------|
| Show HN post | `~/Desktop/first-customer-push/show-hn.md` |
| Reddit posts (r/LocalLLaMA + r/LLMDevs) | `~/Desktop/first-customer-push/reddit-posts.md` |
| Twitter/X thread (6 tweets) | `~/Desktop/first-customer-push/twitter-thread.md` |
| SDK READMEs (rewritten, thorough) | Committed locally |

### Site updates — Waitlist → Live

| Site | Status |
|------|--------|
| `agenttool-landing` | ✅ Built: "Now Live", no waitlist form |
| `agenttool-docs` | ✅ Built: "Coming Soon" → "Live ✅" |
| `agenttool-dashboard` | ✅ Built: billing section + email capture |

### cambridge-tcg

| Item | Status |
|------|--------|
| 2 failing tests (requests mock contamination) | ✅ Fixed (7593e55) — 170/170 pass |

---

## Your sprint checklist (in priority order)

### 🔴 Urgent — RewardsPro (95% uninstall rate)
1. SSH to rp-mktg: `cat /root/.openclaw/workspace/memory/marketing-output.md`
2. Review listing title rewrite + 9 merchant review request emails
3. Approve and deploy

### 🚀 Deploy the overnight builds (30 min)
4. **Cloudflare Pages** — redeploy 3 sites:
   - `agenttool-landing` (push `~/Desktop/agenttool-landing`)
   - `agenttool-docs` (push `~/Desktop/agenttool-docs`)
   - `agenttool-dashboard` (push `~/Desktop/agenttool-dashboard`)
5. **Resend** — sign up at resend.com (free, 100 emails/day)
   - Then: `cd ~/Desktop/agenttool-landing/worker && wrangler secret put RESEND_API_KEY`
   - Redeploy worker: `wrangler deploy`

### 🐙 GitHub SDK repos (15 min)
6. Create two public repos: `agenttool-sdk-py` + `agenttool-sdk-ts`
   - Either via GitHub UI or: create a classic PAT with `repo` scope → I can push automatically
   - READMEs are written and ready

### 📢 Launch (submit when ready)
7. Review `show-hn.md` → submit to Hacker News
   - Best timing: Tue–Thu 9–11am EST (today is Wednesday — **now is the window**)
8. Post to r/LocalLLaMA (reddit-posts.md)
9. Post Twitter thread (twitter-thread.md)

### 🔄 Loop proposal (5 min)
10. Review `cand-002.md` — diagnose-without-deploy gap proposal
    - Path: `~/.openclaw/workspace/memory/loop/proposals/cand-002.md`
    - Low risk: adds `[PP:DEPLOY]` marker to execution protocol

---

## Key URLs (all live)
- Dashboard: https://app.agenttool.dev
- API: https://api.agenttool.dev/health
- Docs: https://docs.agenttool.dev
- Landing: https://agenttool.dev

## Forge access
```bash
ssh root@89.167.84.100
docker ps   # see all 4 services
```

---

_Everything buildable without you is built and deployed. The remaining items are yours._
