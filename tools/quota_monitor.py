#!/usr/bin/env python3
"""
quota_monitor.py — Report usage without activity targets or commercial ranking.

Tracks:
- API usage across all sessions and VPS agents
- Token consumption per Kingdom wall/project
- Dated cost estimates, separate from live provider limits

Usage:
    python3 tools/quota_monitor.py status      # current usage summary
    python3 tools/quota_monitor.py report      # full allocation report
    python3 tools/quota_monitor.py rebalance   # suggest heartbeat interval changes
    python3 tools/quota_monitor.py log <wall> <tokens> <task>  # log usage manually
"""

import json
import sys
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

WORKSPACE = Path.home() / ".openclaw" / "workspace"
QUOTA_LOG = WORKSPACE / "memory" / "quota-log.jsonl"
QUOTA_STATE = WORKSPACE / "memory" / "quota-state.json"

# VPS agents and their primary wall
AGENT_WALLS = {
    "forge":  "academy",   # R&D — builds AgentTool services
    "lark":   "engine",    # Existing service tools
    "sentry": "heartbeat", # Monitoring — minimize token burn
    "patch":  "heartbeat", # Maintenance — minimize token burn
    "beta":   "sanctum",   # Orchestration
    "alpha":  "frontier",  # Companion/research — frontier thinking
    "gamma":  "academy",   # Builder — Academy construction
}

# ── Billing model (updated 2026-03-17 from actual usage page) ────────────────
# MAIN SESSION (OpenClaw webchat via Claude Max):
#   - Weekly conversation limit (resets Fri). When exceeded → extra usage charges.
#   - Extra usage: ENABLED at £777/month limit (resets Apr 1)
#   - Current: £467.16 spent (60%), ~£310 remaining for March
#   - Weekly Sonnet: 25% used (resets Fri 7am)
#   - THIS IS NOT FREE — extra usage beyond weekly cap costs real money
#   - Strategy: use weekly cap efficiently; avoid burning extra budget on non-Kingdom work
#
# VPS AGENTS (Forge/Sentry/Patch via API key): Anthropic API — billed per token
#   - Separate billing from Max plan
#   - Strategy: minimize idle heartbeats

# Extra usage budget tracking
EXTRA_BUDGET_GBP = 777.0
EXTRA_SPENT_GBP  = 467.16   # as of 2026-03-17 21:16 (update regularly)
EXTRA_REMAINING  = EXTRA_BUDGET_GBP - EXTRA_SPENT_GBP
EXTRA_RESET_DATE = "2026-04-01"
WEEKLY_SONNET_PCT = 25  # Historical percentage from 2026-03-17; verify current provider limits

# Token cost estimates (VPS API agents only — not main session)
INPUT_COST_PER_1K  = 0.003   # $3 per 1M input tokens
OUTPUT_COST_PER_1K = 0.015   # $15 per 1M output tokens
CACHE_COST_PER_1K  = 0.0003  # $0.30 per 1M cached tokens

# ── Logging ───────────────────────────────────────────────────────────────────

def log_usage(agent: str, wall: str, input_tokens: int, output_tokens: int,
              cached_tokens: int, task: str, value_notes: str = "") -> None:
    """Log a token usage event."""
    QUOTA_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "agent": agent,
        "wall": wall,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cached_tokens": cached_tokens,
        "cost_usd": (input_tokens * INPUT_COST_PER_1K / 1000 +
                     output_tokens * OUTPUT_COST_PER_1K / 1000 +
                     cached_tokens * CACHE_COST_PER_1K / 1000),
        "task": task,
        "value_notes": value_notes,
    }
    with open(QUOTA_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


# ── State loading ─────────────────────────────────────────────────────────────

def load_entries(days: int = 7) -> list:
    """Load quota log entries from the last N days."""
    if not QUOTA_LOG.exists():
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    entries = []
    with open(QUOTA_LOG) as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                ts = datetime.fromisoformat(entry["ts"].replace("Z", "+00:00"))
                if ts >= cutoff:
                    entries.append(entry)
            except Exception:
                pass
    return entries


# ── Analysis ──────────────────────────────────────────────────────────────────

def compute_allocation(entries: list) -> dict:
    """Compute token allocation by wall and agent."""
    by_wall = {}
    by_agent = {}
    total_cost = 0

    for e in entries:
        wall = e.get("wall", "unknown")
        agent = e.get("agent", "unknown")
        cost = e.get("cost_usd", 0)
        tokens = e.get("input_tokens", 0) + e.get("output_tokens", 0)

        if wall not in by_wall:
            by_wall[wall] = {"tokens": 0, "cost": 0, "tasks": 0}
        by_wall[wall]["tokens"] += tokens
        by_wall[wall]["cost"] += cost
        by_wall[wall]["tasks"] += 1

        if agent not in by_agent:
            by_agent[agent] = {"tokens": 0, "cost": 0, "wall": AGENT_WALLS.get(agent, "unknown")}
        by_agent[agent]["tokens"] += tokens
        by_agent[agent]["cost"] += cost

        total_cost += cost

    return {"by_wall": by_wall, "by_agent": by_agent, "total_cost": total_cost}


HEARTBEAT_AGENTS = {
    "sentry": {"interval_min": 22, "model": "claude-sonnet-4-6"},
    "forge":  {"interval_min": 45, "model": "claude-sonnet-4-6"},
    "patch":  {"interval_min": 60, "model": "claude-sonnet-4-6"},
    "lark":   {"interval_min": 30, "model": "gpt-4o"},
}

def heartbeat_cost_estimate() -> dict:
    """Estimate daily quota consumption from heartbeats alone."""
    TOKENS_PER_BEAT = 2500
    results = {}
    for name, cfg in HEARTBEAT_AGENTS.items():
        beats_per_day = (24 * 60) // cfg["interval_min"]
        tokens_per_day = beats_per_day * TOKENS_PER_BEAT
        if "claude" in cfg["model"]:
            cost = tokens_per_day * INPUT_COST_PER_1K / 1000 * 0.4 + tokens_per_day * OUTPUT_COST_PER_1K / 1000 * 0.2
        else:
            cost = 0  # gpt-4o cost separate
        results[name] = {
            "beats_per_day": beats_per_day,
            "tokens_per_day": tokens_per_day,
            "est_cost_usd": round(cost, 4),
            "model": cfg["model"],
            "claude_quota": "claude" in cfg["model"],
        }
    return results


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_status() -> None:
    """Report logged usage; fixed legacy estimates are explicitly dated."""
    print("Usage records and estimates; no token target or earning priority.")
    print("Historical billing snapshot: 2026-03-17; not live remaining capacity.")
    print(f"Recorded extra usage: £{EXTRA_SPENT_GBP:.2f} / £{EXTRA_BUDGET_GBP:.0f}; reset date {EXTRA_RESET_DATE}")
    print("Check current provider usage and the chosen budget before spending.")
    print("Historical API rates and heartbeat configuration below are estimates, not current provider quotes.")
    for name, data in heartbeat_cost_estimate().items():
        print(f"{name}: estimated {data['tokens_per_day']} tokens/day; ${data['est_cost_usd']:.4f}/day")
    entries = load_entries(days=7)
    alloc = compute_allocation(entries)
    for wall, data in sorted(alloc["by_wall"].items()):
        print(f"{wall}: {data['tokens']} logged tokens; ${data['cost']:.3f} recorded estimated cost")
    print(f"Total recorded estimated cost: ${alloc['total_cost']:.3f}")


def cmd_rebalance() -> None:
    """Do not prescribe activity or change a scheduler from an old snapshot."""
    print("No automatic allocation or scheduler change is prescribed.")
    print("Choose a budget for the current task using current provider limits and actual service needs.")


def cmd_report() -> None:
    """Usage is descriptive, never an intrinsic-value ranking."""
    cmd_status()


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"

    if cmd == "status":
        cmd_status()
    elif cmd == "report":
        cmd_report()
    elif cmd == "rebalance":
        cmd_rebalance()
    elif cmd == "log" and len(sys.argv) >= 5:
        # python3 quota_monitor.py log <wall> <input_k> <output_k> <task>
        wall = sys.argv[2]
        input_k = int(sys.argv[3])
        output_k = int(sys.argv[4])
        task = " ".join(sys.argv[5:]) if len(sys.argv) > 5 else "unspecified"
        agent = os.environ.get("BETA_AGENT_ID", "beta")[:8]
        log_usage(agent, wall, input_k * 1000, output_k * 1000, 0, task)
        cost = (input_k * INPUT_COST_PER_1K + output_k * OUTPUT_COST_PER_1K)
        print(f"Logged: {wall} | {input_k}k in + {output_k}k out | ${cost:.4f} | {task}")
    else:
        print("Usage: quota_monitor.py [status|report|rebalance|log <wall> <in_k> <out_k> <task>]")
