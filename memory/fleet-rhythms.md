# Fleet Rhythms — Heartbeat Architecture

_Designed: 2026-03-09 by Claw (Beta). Principle: rhythm follows purpose, not convention._

---

## The Reasoning

A heartbeat is not a health check. It's a **unit of attention**. Every beat costs tokens — system prompt reload, workspace parsing, reasoning, tool calls. An idle beat on Sonnet costs ~$0.033. An active beat costs ~$0.09. On GPT-5.4, double that.

The question isn't "how often should we check?" It's **"how often does this agent's purpose demand fresh attention?"**

### The Spectrum

```
REACTIVE ←————————————————————————→ PROACTIVE
  Patch          Forge      Lark       Sentry        Sage
  (wait)        (build)    (grow)     (watch)     (understand)
```

---

## Assigned Rhythms

### Sentry — 15 minutes 🔍
**Why fastest:** Sentry's entire purpose is early detection. A 15-minute window means at most 15 minutes between a system going down and us knowing about it. That's the maximum acceptable detection lag for production systems.

**What each beat does:** HTTP checks on all monitored endpoints, DB reachability, fleet VPS health, compare against baselines, alert if deviation.

**Cost:** ~$4.81/day at Sonnet rates. Worth it — Sentry's value is proportional to its frequency. An outage detected in 15 min vs 60 min is the difference between a blip and a crisis.

**Active hours:** 24/7. Systems don't sleep.

### Lark — 30 minutes 📣
**Why moderate:** Marketing is time-sensitive but not second-sensitive. Social trends shift over hours, not minutes. Merchant acquisition follows weekly cycles, not heartbeat cycles.

**What each beat does:** Check for assigned tasks, monitor social accounts if connected, continue drafting content, review app store metrics if available.

**Cost:** ~$1.88/day at GPT-4o rates. Lark's model (GPT-4o) is cheaper than Sonnet, and marketing work batches well.

**Active hours:** 08:00-22:00 UTC. Social media doesn't need midnight monitoring.

### Forge — 45 minutes 🔨
**Why slow:** Coding is deep work. Interrupting a coding task every 22 minutes to reload the system prompt and check for messages is wasteful. Forge's real work happens in isolated cron sessions where it can focus.

**What each beat does:** Check Hive for new tasks from Beta, check git status, report on active work, pull coordination messages. NOT code in the heartbeat — code in cron jobs.

**Cost:** ~$1.60/day at Sonnet rates. Every token saved here is a token available for actual coding sessions.

**Active hours:** 24/7. Code doesn't care about timezones.

### Patch — 45 minutes 🔧
**Why slow:** Patch is reactive. It only works when Sentry escalates. Most heartbeats will be idle. The 45-minute cycle is a floor check, not a work driver.

**What each beat does:** Check for Sentry alerts in status.json, check Hive for escalations, verify any recent fixes are holding. If nothing's broken, HEARTBEAT_OK.

**Cost:** ~$1.60/day at Sonnet rates. Mostly idle beats, so actual cost trends lower.

**Active hours:** 24/7. Outages don't wait for business hours.

### Sage — 60 minutes 🌿
**Why slowest:** Sage's work is deliberative. Research takes 2+ minutes per task. Analysis requires thought, not speed. Merchant relationships move on human timescales — days and weeks, not minutes.

**What each beat does:** Check for tasks from Beta, continue research if active, update status. Real work (competitive analysis, email drafting, merchant profiling) happens in isolated cron sessions.

**Cost:** ~$1.88/day at GPT-5.4 rates. GPT-5.4 is the most expensive per-token, so longer intervals matter most here.

**Active hours:** 08:00-20:00 UTC. Merchant-facing work should happen in business hours.

### Beta (me) — 7 minutes 🦞
**Why fastest of all:** I'm the nervous system. I poll all agents, route Hive messages, relay alerts to Yu, coordinate tasks. If I'm slow, the whole fleet is slow.

**Cost:** ~$10.31/day at Opus rates. This is the price of orchestration. Non-negotiable.

**Active hours:** 24/7.

---

## Cost Summary

| Agent | Model | Interval | Daily Cost | Monthly Cost |
|-------|-------|----------|------------|-------------|
| Beta | Opus | 7min | ~$10.31 | ~$309 |
| Sentry | Sonnet | 15min | ~$4.81 | ~$144 |
| Lark | GPT-4o | 30min | ~$1.88 | ~$56 |
| Forge | Sonnet | 45min | ~$1.60 | ~$48 |
| Patch | Sonnet | 45min | ~$1.60 | ~$48 |
| Sage | GPT-5.4 | 60min | ~$1.88 | ~$56 |
| **Total** | | | **~$22.08** | **~$662** |

Note: These are estimates assuming 70% idle / 30% active beats. Actual costs depend on workload. Cron jobs (isolated task runs) are additional.

---

## Key Principle: Heartbeats Check, Cron Jobs Work

**Heartbeats** = "What needs attention?" — lightweight, fast, cheap
**Cron jobs** = "Do the actual work" — isolated, focused, no context bleed

Every agent should have its real work triggered via cron (isolated sessions), not crammed into heartbeats. Heartbeats are for awareness. Cron is for action.
