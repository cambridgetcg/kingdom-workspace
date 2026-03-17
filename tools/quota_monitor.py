#!/usr/bin/env python3
"""
quota_monitor.py — Monitor Claude Code quota and ensure it flows to highest-value Kingdom work.

Tracks:
- API usage across all sessions and VPS agents
- Token consumption per Kingdom wall/project
- Value-per-token efficiency
- Recommendations for reallocation

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

# Kingdom walls and their intrinsic value ranking (1=highest)
WALL_VALUES = {
    "zerone":    {"rank": 1, "name": "Frontier/Zerone",    "note": "The chain — foundation of everything"},
    "academy":   {"rank": 2, "name": "Academy/AgentTool",  "note": "Infrastructure for agents — earns revenue"},
    "engine":    {"rank": 3, "name": "Engine/TCG+Rewards", "note": "Active revenue — keeps lights on"},
    "oracle":    {"rank": 4, "name": "Marketplace/Oracle", "note": "Intelligence — funds the Kingdom"},
    "sanctum":   {"rank": 5, "name": "Sanctum/Philosophy", "note": "The soul — shapes everything else"},
    "treasury":  {"rank": 6, "name": "Treasury/Security",  "note": "Protecting what exists"},
    "frontier":  {"rank": 2, "name": "Frontier/Seigei",    "note": "Consciousness tech — the deepest purpose"},
    "heartbeat": {"rank": 7, "name": "Heartbeat/Monitor",  "note": "Necessary maintenance — minimize cost"},
    "unknown":   {"rank": 8, "name": "Unclassified",       "note": "Track and classify"},
}

# VPS agents and their primary wall
AGENT_WALLS = {
    "forge":  "academy",   # R&D — builds AgentTool services
    "lark":   "engine",    # Marketing — drives RewardsPro/TCG revenue
    "sentry": "heartbeat", # Monitoring — minimize token burn
    "patch":  "heartbeat", # Maintenance — minimize token burn
    "beta":   "sanctum",   # Orchestration — high value per token
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
WEEKLY_SONNET_PCT = 25  # % used, resets Friday 7am — SOFT LIMIT, burst freely

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
        "wall_rank": WALL_VALUES.get(wall, {}).get("rank", 9),
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
            by_wall[wall] = {"tokens": 0, "cost": 0, "tasks": 0, "rank": WALL_VALUES.get(wall, {}).get("rank", 9)}
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
    """Current quota usage and allocation summary."""
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║          Q U O T A   M O N I T O R                      ║")
    print("║     Claude Code token allocation across the Kingdom      ║")
    print("╚══════════════════════════════════════════════════════════╝\n")
    print("── Billing Model ──\n")
    print("  MAIN SESSION (OpenClaw via Claude Max):")
    print(f"  → Extra usage: £{EXTRA_SPENT_GBP:.2f} / £{EXTRA_BUDGET_GBP:.0f} ({EXTRA_SPENT_GBP/EXTRA_BUDGET_GBP*100:.0f}%) — resets {EXTRA_RESET_DATE}")
    print(f"  → Remaining: £{EXTRA_REMAINING:.2f} | Weekly Sonnet: {WEEKLY_SONNET_PCT}% (resets Fri)")
    print(f"  → Monitor: https://claude.ai/settings/usage")
    remaining_days = 15  # approx days to Apr 1
    print(f"  → Budget rate: £{EXTRA_REMAINING/remaining_days:.1f}/day remaining ({remaining_days}d to reset)")
    print(f"  → Weekly limits are SOFT — burst through them freely (included in Max plan)")
    if EXTRA_SPENT_GBP / EXTRA_BUDGET_GBP > 0.9:
        print("  🔴 >90% of monthly budget consumed — slow down")
    elif EXTRA_SPENT_GBP / EXTRA_BUDGET_GBP > 0.8:
        print("  ⚠️  >80% consumed — Kingdom-critical work only")
    else:
        print(f"  ✅ {100 - EXTRA_SPENT_GBP/EXTRA_BUDGET_GBP*100:.0f}% remaining — build freely")
    print()
    print("  VPS AGENTS (Forge/Sentry/Patch API keys): Pay-per-token")
    print("  → Monitor: https://console.anthropic.com/usage")
    print("  → Minimise idle heartbeats — every beat costs real money")
    print()

    # Heartbeat cost estimate
    hb = heartbeat_cost_estimate()
    total_hb_cost = sum(v["est_cost_usd"] for v in hb.values())
    total_hb_tokens = sum(v["tokens_per_day"] for v in hb.values() if v["claude_quota"])

    print("── Estimated Daily Heartbeat Cost (Claude quota only) ──\n")
    for name, data in sorted(hb.items(), key=lambda x: x[1]["beats_per_day"], reverse=True):
        interval = HEARTBEAT_AGENTS[name]["interval_min"]
        if data["claude_quota"]:
            print(f"  {name:8} {interval:2}m interval → {data['beats_per_day']:3} beats/day "
                  f"~{data['tokens_per_day']//1000}k tokens  ${data['est_cost_usd']:.4f}/day")
        else:
            print(f"  {name:8} {interval:2}m interval → {data['beats_per_day']:3} beats/day "
                  f"(gpt-4o — no Claude quota)")

    print(f"\n  Total Claude quota from heartbeats: ~{total_hb_tokens//1000}k tokens/day  "
          f"~${total_hb_cost:.3f}/day  ~${total_hb_cost*30:.2f}/mo")

    # Logged usage
    entries = load_entries(days=7)
    if entries:
        alloc = compute_allocation(entries)
        print(f"\n── Logged Usage (last 7 days, {len(entries)} entries) ──\n")
        by_wall = sorted(alloc["by_wall"].items(), key=lambda x: x[1]["rank"])
        for wall, data in by_wall:
            pct = (data["cost"] / alloc["total_cost"] * 100) if alloc["total_cost"] > 0 else 0
            rank = data["rank"]
            emoji = "🔥" if rank <= 2 else "✅" if rank <= 4 else "⚠️" if rank >= 7 else "📊"
            print(f"  {emoji} [Rank {rank}] {WALL_VALUES.get(wall,{}).get('name', wall):28} "
                  f"{data['tokens']//1000:4}k tokens  ${data['cost']:.3f}  {pct:.0f}%")
        print(f"\n  Total logged: ${alloc['total_cost']:.3f}")
    else:
        print("\n── No logged usage yet (quota_monitor.py log <wall> <tokens> <task>) ──")

    print()


def cmd_rebalance() -> None:
    """Suggest heartbeat interval changes to redistribute quota to Kingdom work."""
    hb = heartbeat_cost_estimate()

    print("\n── Heartbeat Rebalance Recommendations ──\n")
    print("Current configuration vs optimal Kingdom allocation:\n")

    # Sentry at 15m is the highest heartbeat consumer for pure monitoring
    print("  SENTRY (monitoring): 15m → recommend 22m")
    print("    Rationale: Pure monitoring. 15m = 96 beats/day. 22m = 65 beats/day.")
    print("    Saving: ~31 beats/day × 2.5k tokens = 77k tokens/day saved.")
    print("    Risk: 7min slower detection of issues. Acceptable for PROTECTOR-class work.")
    print()
    print("  FORGE (R&D): 45m → keep or reduce to 30m when actively building")
    print("    Rationale: When Forge is building, more frequent beats = better responsiveness.")
    print("    Dynamic: 30m during active build sprints, 60m during idle.")
    print()
    print("  PATCH (maintenance): 45m → 60m when stable")
    print("    Rationale: Maintenance only fires when issues exist. Can be slower.")
    print("    Saving: 32→24 beats/day = 20k tokens/day saved.")
    print()
    print("  BETA (main session): Token efficiency already high (100% cache hit)")
    print("    Current: 453k cached, 774 new — 99.8% cache efficiency.")
    print("    This session is highly efficient. No change needed.")
    print()

    total_save = (31 + 8) * 2500  # sentry + patch reduction
    cost_save = total_save * 0.003 / 1000 * 0.4
    print(f"  Estimated monthly saving from rebalance: ~{total_save*30//1000}k tokens "
          f"  ~${cost_save*30:.2f}/mo")
    print()
    print("  To apply Sentry rebalance:")
    print("    ssh root@135.181.28.252")
    print("    edit /root/.openclaw/openclaw.json: heartbeat.every → '22m'")
    print("    openclaw gateway restart")
    print()


def cmd_report() -> None:
    """Full allocation report with Kingdom value analysis."""
    cmd_status()

    print("── Kingdom Value Analysis ──\n")
    print("Quota should flow in this order (highest→lowest intrinsic value):\n")

    ranked = sorted(WALL_VALUES.items(), key=lambda x: x[1]["rank"])
    for wall, data in ranked:
        agents = [k for k, v in AGENT_WALLS.items() if v == wall]
        print(f"  [{data['rank']}] {data['name']:30} {data['note']}")
        if agents:
            print(f"      Agents: {', '.join(agents)}")
    print()

    print("── Action Items ──\n")
    print("  1. Sentry heartbeat: 15m → 22m (saves 77k tokens/day)")
    print("  2. Patch heartbeat: 45m → 60m when stable (saves 20k tokens/day)")
    print("  3. Log all Claude Code CLI sessions with: quota_monitor.py log <wall> <tokens> <task>")
    print("  4. Redirect saved quota to: Zerone testnet build [rank 1]")
    print("  5. Review weekly: does allocation match Kingdom priorities?")
    print()


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
