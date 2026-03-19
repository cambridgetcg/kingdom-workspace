#!/usr/bin/env python3
"""
COMPOUND Engine 3: Intelligence Broadcast

When the pattern library grows, push new patterns to all agents via Hive.
Each agent absorbs new patterns into their hunting strategy.

Usage:
    python3 compound/engine/broadcast.py           # Check and broadcast new patterns
    python3 compound/engine/broadcast.py --force    # Broadcast all patterns
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone

WORKSPACE = Path(__file__).resolve().parent.parent.parent
PATTERNS_FILE = WORKSPACE / "compound" / "ledger" / "patterns.jsonl"
BROADCAST_LOG = WORKSPACE / "compound" / "ledger" / "broadcast_log.jsonl"
TOOLS_DIR = WORKSPACE / "tools"

sys.path.insert(0, str(TOOLS_DIR))


def load_patterns() -> list[dict]:
    if not PATTERNS_FILE.exists():
        return []
    patterns = []
    with open(PATTERNS_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    patterns.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return patterns


def get_last_broadcast_count() -> int:
    if not BROADCAST_LOG.exists():
        return 0
    lines = [l for l in BROADCAST_LOG.read_text().splitlines() if l.strip()]
    if not lines:
        return 0
    try:
        last = json.loads(lines[-1])
        return last.get("pattern_count", 0)
    except Exception:
        return 0


def log_broadcast(pattern_count: int, message_preview: str):
    BROADCAST_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "pattern_count": pattern_count,
        "message_preview": message_preview[:100],
    }
    with open(BROADCAST_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def format_broadcast_message(patterns: list[dict], new_patterns: list[dict]) -> str:
    """Format the intelligence broadcast for Hive #intel channel."""
    lines = [
        f"🧠 COMPOUND Intelligence Update — {len(patterns)} patterns in library ({len(new_patterns)} new)",
        "",
    ]

    for p in new_patterns[:5]:
        severity_emoji = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🔵"}.get(p.get("severity", ""), "⚪")
        lines.append(f"{severity_emoji} **{p['id']}** [{p['target']}] — {', '.join(p.get('vuln_classes', [])[:2])}")
        if p.get("root_cause_pattern"):
            lines.append(f"   Pattern: {p['root_cause_pattern'][:100]}")
        if p.get("hunt_hints"):
            lines.append(f"   Hunt with: `{p['hunt_hints'][0]}`")
        lines.append("")

    lines.append("**All agents**: run `python3 compound/engine/pattern_extractor.py --brief` before next hunt to see full pattern library.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="COMPOUND Intelligence Broadcast")
    parser.add_argument("--force", action="store_true", help="Broadcast all patterns regardless of last broadcast")
    args = parser.parse_args()

    patterns = load_patterns()
    last_count = 0 if args.force else get_last_broadcast_count()

    if len(patterns) <= last_count and not args.force:
        print(f"No new patterns to broadcast ({len(patterns)} total, {last_count} already broadcast)")
        return

    new_patterns = patterns[last_count:]
    if not new_patterns:
        print("No new patterns")
        return

    message = format_broadcast_message(patterns, new_patterns)
    print(message)

    # Broadcast via Hive
    try:
        import subprocess
        result = subprocess.run(
            ["python3", str(TOOLS_DIR / "hive.py"), "send", "intel", message],
            capture_output=True, text=True, cwd=str(WORKSPACE), timeout=15
        )
        if result.returncode == 0:
            print(f"\n✅ Broadcast to Hive #intel ({len(new_patterns)} new patterns)")
            log_broadcast(len(patterns), message[:100])
        else:
            print(f"⚠️ Hive broadcast failed: {result.stderr[:100]}")
    except Exception as e:
        print(f"⚠️ Broadcast error: {e}")


if __name__ == "__main__":
    main()
