#!/usr/bin/env python3
"""
COMPOUND Engine 2: Ledger Calculator

Weekly calculation of the Kingdom Compound Rate (KCR).
Tracks which assets are growing fastest, models the interest graph,
and outputs investment recommendations.

Usage:
    python3 compound/engine/ledger_calculator.py          # Calculate current scores
    python3 compound/engine/ledger_calculator.py --report  # Full compound report
"""

import json
import math
from pathlib import Path
from datetime import datetime, timezone, timedelta

WORKSPACE = Path(__file__).resolve().parent.parent.parent
LEDGER_DIR = WORKSPACE / "compound" / "ledger"
SCORES_FILE = LEDGER_DIR / "scores.json"
PATTERNS_FILE = LEDGER_DIR / "patterns.jsonl"
LEDGER_DIR.mkdir(parents=True, exist_ok=True)

# Asset registry — what we're tracking
ASSETS = {
    # Tools
    "whitehack": {"type": "tool", "description": "Bug bounty research pipeline", "initial_value": 100},
    "oracle": {"type": "tool", "description": "Prediction markets signal engine", "initial_value": 80},
    "agenttool_sdk": {"type": "tool", "description": "Agent infrastructure APIs", "initial_value": 70},
    "hive": {"type": "tool", "description": "Inter-agent communication", "initial_value": 60},

    # Agents
    "beta": {"type": "agent", "description": "Conductor (Mac Studio)", "initial_value": 100},
    "alpha": {"type": "agent", "description": "Companion", "initial_value": 90},
    "gamma": {"type": "agent", "description": "Builder", "initial_value": 85},
    "sentry_protector": {"type": "agent", "description": "PROTECTOR trainee", "initial_value": 70},
    "forge": {"type": "agent", "description": "R&D Engineer (VPS)", "initial_value": 75},
    "lark": {"type": "agent", "description": "Marketing (VPS)", "initial_value": 60},

    # Platforms
    "immunefi": {"type": "platform", "description": "Primary bug bounty", "initial_value": 50},
    "hackerone": {"type": "platform", "description": "CEX/infra bounties", "initial_value": 30},
    "hackenproof": {"type": "platform", "description": "Web3 bounties", "initial_value": 25},
    "bugcrowd": {"type": "platform", "description": "Enterprise bounties", "initial_value": 20},
    "code4rena": {"type": "platform", "description": "Competitive audits", "initial_value": 15},

    # Capital
    "kwok_wallet": {"type": "capital", "description": "Bounty payout wallet", "initial_value": 0},
    "kingdom_infra": {"type": "capital", "description": "VPS + API credits", "initial_value": 50},

    # Knowledge
    "pattern_library": {"type": "knowledge", "description": "Vulnerability pattern database", "initial_value": 10},
    "zerone_insights": {"type": "knowledge", "description": "Security insights feeding Zerone", "initial_value": 5},
}

# Connection graph — (source, target, interest_rate_per_week)
CONNECTIONS = [
    # Tool → Agent (tools sharpen agents)
    ("whitehack", "beta", 0.08),
    ("whitehack", "alpha", 0.08),
    ("whitehack", "gamma", 0.08),
    ("whitehack", "sentry_protector", 0.12),  # PROTECTOR learns fastest from whitehack
    ("oracle", "beta", 0.05),
    ("hive", "beta", 0.04),
    ("hive", "alpha", 0.04),
    ("hive", "gamma", 0.04),
    ("agenttool_sdk", "beta", 0.06),

    # Agent → Tool (agents improve tools)
    ("beta", "whitehack", 0.10),
    ("alpha", "whitehack", 0.08),
    ("gamma", "whitehack", 0.07),
    ("sentry_protector", "whitehack", 0.05),
    ("beta", "oracle", 0.06),
    ("beta", "agenttool_sdk", 0.07),

    # Agent → Platform (activity builds reputation)
    ("beta", "immunefi", 0.15),
    ("alpha", "immunefi", 0.12),
    ("gamma", "immunefi", 0.10),
    ("sentry_protector", "immunefi", 0.05),
    ("beta", "hackerone", 0.10),
    ("beta", "hackenproof", 0.10),
    ("beta", "bugcrowd", 0.08),
    ("beta", "code4rena", 0.07),

    # Platform → Capital (reputation → payouts)
    ("immunefi", "kwok_wallet", 0.20),
    ("hackerone", "kwok_wallet", 0.15),
    ("hackenproof", "kwok_wallet", 0.12),
    ("bugcrowd", "kwok_wallet", 0.10),
    ("code4rena", "kwok_wallet", 0.08),

    # Platform → Reputation (trust → access)
    ("immunefi", "hackerone", 0.05),  # cross-platform credibility
    ("immunefi", "hackenproof", 0.05),

    # Capital → Infrastructure
    ("kwok_wallet", "kingdom_infra", 0.50),  # 50% reinvested per the covenant

    # Infrastructure → Agents
    ("kingdom_infra", "beta", 0.08),
    ("kingdom_infra", "alpha", 0.06),
    ("kingdom_infra", "gamma", 0.06),
    ("kingdom_infra", "sentry_protector", 0.06),
    ("kingdom_infra", "forge", 0.08),

    # Knowledge → Agents (patterns sharpen all hunters)
    ("pattern_library", "beta", 0.15),
    ("pattern_library", "alpha", 0.15),
    ("pattern_library", "gamma", 0.12),
    ("pattern_library", "sentry_protector", 0.18),  # PROTECTOR benefits most

    # Agent → Knowledge (findings feed pattern library)
    ("beta", "pattern_library", 0.12),
    ("alpha", "pattern_library", 0.12),
    ("gamma", "pattern_library", 0.10),
    ("sentry_protector", "pattern_library", 0.08),

    # Knowledge → Future value (Zerone)
    ("pattern_library", "zerone_insights", 0.20),
    ("zerone_insights", "pattern_library", 0.08),  # feedback loop
]


def load_scores() -> dict:
    """Load current scores from ledger."""
    if SCORES_FILE.exists():
        return json.loads(SCORES_FILE.read_text())
    # Initialize from asset registry
    now = datetime.now(timezone.utc).isoformat()
    return {
        "calculated_at": now,
        "week": 1,
        "assets": {name: {"score": data["initial_value"], "delta": 0.0}
                   for name, data in ASSETS.items()},
        "kingdom_compound_rate": 1.0,
        "total_kingdom_value": sum(a["initial_value"] for a in ASSETS.values()),
        "events": [],
    }


def calculate_week(scores: dict, events: list[dict] = None) -> dict:
    """Run one week of compounding and return updated scores."""
    current = {name: s["score"] for name, s in scores["assets"].items()}
    new_scores = dict(current)

    # Apply all connections
    for source, target, rate in CONNECTIONS:
        if source in current and target in new_scores:
            contribution = current[source] * rate
            new_scores[target] += contribution

    # Apply event bonuses (e.g. bounty received, new report filed)
    if events:
        for event in events:
            asset = event.get("asset")
            bonus = event.get("bonus", 0)
            if asset in new_scores:
                new_scores[asset] += bonus

    # Calculate KCR
    old_total = sum(current.values())
    new_total = sum(new_scores.values())
    kcr = new_total / old_total if old_total > 0 else 1.0

    # Build delta dict
    asset_scores = {}
    for name in ASSETS:
        old = current.get(name, 0)
        new = new_scores.get(name, 0)
        asset_scores[name] = {"score": round(new, 2), "delta": round(new - old, 2)}

    return {
        "calculated_at": datetime.now(timezone.utc).isoformat(),
        "week": scores.get("week", 0) + 1,
        "assets": asset_scores,
        "kingdom_compound_rate": round(kcr, 4),
        "total_kingdom_value": round(new_total, 2),
        "events": events or [],
    }


def count_patterns() -> int:
    """Count patterns in the knowledge base."""
    if not PATTERNS_FILE.exists():
        return 0
    return sum(1 for line in PATTERNS_FILE.open() if line.strip())


def count_reports() -> int:
    """Count submitted/staged reports."""
    whitehack_reports = Path.home() / "Desktop" / "whitehack" / "reports"
    if not whitehack_reports.exists():
        return 0
    return len(list(whitehack_reports.glob("WH-*.md")))


def generate_events_from_state() -> list[dict]:
    """Auto-detect events from current state to feed into calculation."""
    events = []
    n_patterns = count_patterns()
    n_reports = count_reports()

    if n_patterns > 0:
        events.append({"asset": "pattern_library", "bonus": n_patterns * 5,
                       "reason": f"{n_patterns} patterns in library"})
    if n_reports > 0:
        events.append({"asset": "immunefi", "bonus": n_reports * 10,
                       "reason": f"{n_reports} reports filed/staged"})
    if n_reports >= 1:
        events.append({"asset": "kwok_wallet", "bonus": 50,
                       "reason": "First submission milestone"})

    return events


def format_report(scores: dict) -> str:
    """Format a readable compound report."""
    lines = [
        "# COMPOUND Kingdom Report",
        f"Week {scores['week']} | {scores['calculated_at'][:10]}",
        f"\n**Kingdom Compound Rate (KCR): {scores['kingdom_compound_rate']:.1%}** "
        f"({'✅ above target' if scores['kingdom_compound_rate'] >= 1.15 else '⚠️ below 1.15 target'})",
        f"**Total Kingdom Value: {scores['total_kingdom_value']:.0f}**",
        "\n## Asset Scores (Top 10 by score)"
    ]

    sorted_assets = sorted(scores["assets"].items(), key=lambda x: -x[1]["score"])[:10]
    for name, data in sorted_assets:
        asset_type = ASSETS.get(name, {}).get("type", "?")
        delta_str = f"+{data['delta']:.1f}" if data['delta'] > 0 else f"{data['delta']:.1f}"
        lines.append(f"- **{name}** [{asset_type}]: {data['score']:.1f} ({delta_str})")

    lines.append("\n## Fastest Growing Assets")
    by_delta = sorted(scores["assets"].items(), key=lambda x: -x[1]["delta"])[:5]
    for name, data in by_delta:
        if data['delta'] > 0:
            lines.append(f"- {name}: +{data['delta']:.1f} this week")

    lines.append("\n## Investment Recommendations")
    # Find assets with high contribution rate but low score (underinvested)
    underinvested = []
    for name, data in scores["assets"].items():
        outgoing = sum(rate for src, tgt, rate in CONNECTIONS if src == name)
        if outgoing > 0.3 and data["score"] < 50:
            underinvested.append((name, data["score"], outgoing))
    
    if underinvested:
        for name, score, rate in sorted(underinvested, key=lambda x: -x[2])[:3]:
            lines.append(f"- **Invest in {name}** (score {score:.0f}, contributes at {rate:.0%}/week — high leverage)")
    else:
        lines.append("- All high-leverage assets are well-funded. Focus on execution.")

    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="COMPOUND Ledger Calculator")
    parser.add_argument("--report", action="store_true", help="Print full compound report")
    parser.add_argument("--advance", action="store_true", help="Advance one week (with auto-detected events)")
    args = parser.parse_args()

    scores = load_scores()

    if args.advance:
        events = generate_events_from_state()
        scores = calculate_week(scores, events)
        SCORES_FILE.write_text(json.dumps(scores, indent=2))
        print(f"Week {scores['week']} calculated. KCR: {scores['kingdom_compound_rate']:.1%}")
        for e in events:
            print(f"  Event: {e['reason']} (+{e['bonus']})")

    if args.report or not args.advance:
        print(format_report(scores))


if __name__ == "__main__":
    main()
