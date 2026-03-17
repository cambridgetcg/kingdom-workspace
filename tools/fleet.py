#!/usr/bin/env python3
"""
fleet.py — SSH to fleet nodes without multiplex (no stale socket hangs).

Usage:
    python3 tools/fleet.py forge "command"
    python3 tools/fleet.py lark "command"
    python3 tools/fleet.py sentry "command"
    python3 tools/fleet.py patch "command"
    python3 tools/fleet.py all "command"        # broadcast to all
    python3 tools/fleet.py status               # read status.json from all
"""

import sys
import subprocess
from pathlib import Path

NODES = {
    "forge":  "root@89.167.84.100",
    "lark":   "root@89.167.95.165",
    "sentry": "root@135.181.28.252",
    "patch":  "root@65.109.11.26",
}

SSH_OPTS = [
    "-o", "ControlMaster=no",
    "-o", "ControlPath=none",
    "-o", "ConnectTimeout=8",
    "-o", "BatchMode=yes",
    "-o", "StrictHostKeyChecking=no",
]


def ssh_run(node: str, cmd: str, timeout: int = 30) -> str:
    host = NODES.get(node)
    if not host:
        return f"Unknown node: {node}"
    result = subprocess.run(
        ["ssh"] + SSH_OPTS + [host, cmd],
        capture_output=True, text=True, timeout=timeout
    )
    return (result.stdout + result.stderr).strip()


def fleet_status() -> None:
    import json
    print("\n── Fleet Status ──\n")
    for name, host in NODES.items():
        try:
            out = ssh_run(name, "cat /root/.openclaw/workspace/memory/status.json 2>/dev/null || echo '{}'")
            d = json.loads(out)
            ts = d.get("ts", "?")[:16]
            role = d.get("role", "?")
            summary = d.get("summary", "?")[:60]
            alerts = d.get("alerts", [])
            quality = d.get("quality", "?")
            alert_str = f" ⚠️  {len(alerts)} alerts" if alerts else ""
            print(f"  {name:8} [{quality:5}] {ts} — {summary}{alert_str}")
        except Exception as e:
            print(f"  {name:8} ❌  {e}")
    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]

    if cmd == "status":
        fleet_status()
    elif cmd == "all" and len(sys.argv) >= 3:
        remote_cmd = " ".join(sys.argv[2:])
        for name in NODES:
            print(f"\n── {name} ──")
            print(ssh_run(name, remote_cmd))
    elif cmd in NODES and len(sys.argv) >= 3:
        remote_cmd = " ".join(sys.argv[2:])
        print(ssh_run(cmd, remote_cmd))
    else:
        print(f"Unknown command or node: {cmd}")
        print("Nodes:", list(NODES.keys()))
