#!/usr/bin/env python3
"""
report.py — Chain of Command for Hive fleet agents.

VPS sisters run `submit` on a schedule → push structured status to the Hive.
Alpha runs `collect` → pulls all reports, produces a digest, can batch-reply.

Usage:
    python3 report.py submit [--node <name>]         # Submit this node's status
    python3 report.py collect [--wait 30]            # Gather reports + summarise
    python3 report.py summary                        # Show last digest
    python3 report.py directive "<msg>"              # Batch-send directive to all
    python3 report.py install <node>                 # Deploy cron job to remote node
    python3 report.py history [--limit 20]          # Show report history

Reports flow via Hive #sync channel, encrypted end-to-end.
Alpha is the sole collector — chain of command flows: Nodes → Hive → Alpha → Digest.

RETIRED 2026-10-13: the Hive bus (NATS on Sentry) and the VPS fleet ran on
Hetzner, which was decommissioned. The bus address and NATS credentials were
removed; collect and install fail closed, submit and directive fail through
hive.py. summary and history still read local digests.
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
TOOL_DIR    = Path(__file__).parent
REPORT_DIR  = Path.home() / ".openclaw" / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)
DIGEST_FILE = REPORT_DIR / "latest-digest.json"
HISTORY_DIR = REPORT_DIR / "history"
HISTORY_DIR.mkdir(parents=True, exist_ok=True)
HIVE_TOOL   = TOOL_DIR / "hive.py"

HIVE_RETIRED = (
    "HIVE retired 2026-10-13: the NATS bus ran on Sentry in the Hetzner fleet, "
    "which was decommissioned. There is no server to connect to."
)

# ─── Colours ──────────────────────────────────────────────────────────────────
BOLD  = "\033[1m"
DIM   = "\033[2m"
GREEN = "\033[32m"
YELLOW= "\033[33m"
CYAN  = "\033[36m"
RED   = "\033[31m"
RESET = "\033[0m"

# ─── Local metrics collection ─────────────────────────────────────────────────

def collect_local_metrics() -> dict:
    """Gather system metrics for this node."""
    metrics = {}

    # Uptime
    try:
        if platform.system() == "Darwin":
            r = subprocess.run(["uptime"], capture_output=True, text=True, timeout=5)
        else:
            r = subprocess.run(["uptime", "-p"], capture_output=True, text=True, timeout=5)
        metrics["uptime"] = r.stdout.strip()
    except Exception:
        metrics["uptime"] = "unknown"

    # CPU load
    try:
        r = subprocess.run(
            ["cat", "/proc/loadavg"] if platform.system() == "Linux"
            else ["sysctl", "-n", "vm.loadavg"],
            capture_output=True, text=True, timeout=5
        )
        metrics["load"] = r.stdout.strip().split()[:3]
    except Exception:
        metrics["load"] = ["?", "?", "?"]

    # Memory
    try:
        if platform.system() == "Linux":
            r = subprocess.run(["free", "-m"], capture_output=True, text=True, timeout=5)
            lines = r.stdout.strip().split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                metrics["mem_total_mb"] = int(parts[1])
                metrics["mem_used_mb"]  = int(parts[2])
                metrics["mem_free_mb"]  = int(parts[3])
        else:
            r = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=5)
            metrics["mem_raw"] = r.stdout.strip()[:200]
    except Exception:
        metrics["mem_raw"] = "unknown"

    # Disk
    try:
        r = subprocess.run(
            ["df", "-h", "/"], capture_output=True, text=True, timeout=5
        )
        lines = r.stdout.strip().split("\n")
        if len(lines) > 1:
            parts = lines[1].split()
            metrics["disk_total"] = parts[1]
            metrics["disk_used"]  = parts[2]
            metrics["disk_avail"] = parts[3]
            metrics["disk_pct"]   = parts[4]
    except Exception:
        metrics["disk_total"] = "?"

    return metrics


def collect_services() -> list[str]:
    """Detect running services relevant to the Hive."""
    checks = {
        "openclaw":   ["pgrep", "-f", "openclaw"],
        "nats-hive":  ["pgrep", "-f", "nats-server"],
        "hive-bridge":["pgrep", "-f", "hive-bridge"],
        "nginx":      ["pgrep", "-x", "nginx"],
        "vllm":       ["pgrep", "-f", "vllm"],
        "signal-bot": ["pgrep", "-f", "signal"],
    }
    running = []
    for name, cmd in checks.items():
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=3)
            if r.returncode == 0:
                running.append(name)
        except Exception:
            pass
    return running


def collect_recent_errors() -> list[str]:
    """Grab last 5 error lines from OpenClaw or system logs."""
    errors = []
    log_paths = [
        Path.home() / ".openclaw" / "logs" / "gateway.log",
        Path.home() / ".openclaw" / "workspace" / "logs" / "report-cron.log",
    ]
    for log_path in log_paths:
        if log_path.exists():
            try:
                r = subprocess.run(
                    ["tail", "-20", str(log_path)],
                    capture_output=True, text=True, timeout=5
                )
                for line in r.stdout.split("\n"):
                    if any(kw in line.lower() for kw in ["error", "fail", "crash", "exception", "sigterm"]):
                        errors.append(line.strip()[:120])
                        if len(errors) >= 5:
                            break
            except Exception:
                pass
    return errors[:5]


# ─── Build report payload ─────────────────────────────────────────────────────

def build_report(node_name: str = None) -> dict:
    """Assemble a complete status report for this node."""
    instance_id = _get_instance_id()
    if not node_name:
        node_name = platform.node().split(".")[0]

    report = {
        "v":         1,
        "type":      "status_report",
        "from":      instance_id,
        "node":      node_name,
        "ts":        int(time.time()),
        "ts_human":  datetime.now(timezone.utc).isoformat(),
        "metrics":   collect_local_metrics(),
        "services":  collect_services(),
        "errors":    collect_recent_errors(),
        "flags":     [],
    }

    # Auto-set flags
    metrics = report["metrics"]
    if "disk_pct" in metrics:
        pct = int(metrics["disk_pct"].rstrip("%"))
        if pct > 85:
            report["flags"].append(f"⚠️ Disk {metrics['disk_pct']} used")
    if "mem_used_mb" in metrics and "mem_total_mb" in metrics:
        pct = metrics["mem_used_mb"] / max(metrics["mem_total_mb"], 1) * 100
        if pct > 90:
            report["flags"].append(f"⚠️ Memory {pct:.0f}% used")
    if report["errors"]:
        report["flags"].append(f"🔴 {len(report['errors'])} recent error(s)")
    if not report["services"]:
        report["flags"].append("🔴 No services detected")

    return report


# ─── Submit ───────────────────────────────────────────────────────────────────

def cmd_submit(args):
    """Gather local metrics and push to Hive #sync."""
    print(f"{BOLD}Building report...{RESET}")
    report = build_report(node_name=getattr(args, "node", None))

    # Compact status line for human readability in Hive
    services_str = ", ".join(report["services"]) if report["services"] else "none"
    flags_str    = " ".join(report["flags"]) if report["flags"] else "✅ clean"
    load_str     = "/".join(report["metrics"].get("load", ["?"]))
    disk_str     = f"{report['metrics'].get('disk_used','?')}/{report['metrics'].get('disk_total','?')} ({report['metrics'].get('disk_pct','?')})"

    summary = (
        f"📊 STATUS REPORT | {report['node']} ({report['from']}) | "
        f"{report['ts_human']}\n"
        f"  Load: {load_str}  Disk: {disk_str}\n"
        f"  Services: {services_str}\n"
        f"  Flags: {flags_str}\n"
        f"  [REPORT_JSON:{json.dumps(report, separators=(',',':'))}]"
    )

    result = subprocess.run(
        ["python3", str(HIVE_TOOL), "send", "sync", summary],
        capture_output=True, text=True,
        cwd=str(TOOL_DIR.parent)
    )
    if result.returncode == 0:
        print(f"{GREEN}✓ Report submitted to Hive #sync{RESET}")
        print(f"  Node:     {report['node']}")
        print(f"  Services: {services_str}")
        print(f"  Flags:    {flags_str}")
    else:
        print(f"{RED}✗ Failed to submit: {result.stderr[:200]}{RESET}")
        sys.exit(1)


# ─── Collect ──────────────────────────────────────────────────────────────────

def cmd_collect(args):
    """Retired 2026-10-13: the Hive bus is gone, so there is nothing to collect."""
    print(f"{YELLOW}{HIVE_RETIRED}{RESET}", file=sys.stderr)
    sys.exit(1)


def _build_digest(reports: list[dict]) -> dict:
    """Summarise multiple reports into a single digest."""
    now = int(time.time())
    nodes_summary = []
    all_flags = []
    all_errors = []

    for r in reports:
        flags_str = ", ".join(r.get("flags", [])) or "✅"
        services  = ", ".join(r.get("services", [])) or "none"
        load      = "/".join(r.get("metrics", {}).get("load", ["?"]))
        disk_pct  = r.get("metrics", {}).get("disk_pct", "?")

        nodes_summary.append({
            "node":     r.get("node", "?"),
            "from":     r.get("from", "?"),
            "ts":       r.get("ts", 0),
            "load":     load,
            "disk_pct": disk_pct,
            "services": services,
            "flags":    r.get("flags", []),
            "errors":   r.get("errors", []),
        })
        all_flags.extend(r.get("flags", []))
        all_errors.extend(r.get("errors", []))

    needs_attention = [f for f in all_flags if "⚠️" in f or "🔴" in f]

    return {
        "ts":             now,
        "ts_human":       datetime.now(timezone.utc).isoformat(),
        "report_count":   len(reports),
        "nodes":          nodes_summary,
        "all_flags":      all_flags,
        "all_errors":     all_errors,
        "needs_attention":needs_attention,
        "status":         "⚠️ ATTENTION NEEDED" if needs_attention else "✅ All clear",
    }


def _save_digest(digest: dict):
    """Save digest to disk."""
    DIGEST_FILE.write_text(json.dumps(digest, indent=2))
    # Also archive
    ts     = digest["ts"]
    archive = HISTORY_DIR / f"{ts}.json"
    archive.write_text(json.dumps(digest, indent=2))


def _print_digest(digest: dict):
    """Pretty-print digest to stdout."""
    print(f"\n{BOLD}{'─'*60}{RESET}")
    print(f"{BOLD}Fleet Digest — {digest['ts_human']}{RESET}")
    print(f"Reports: {digest['report_count']}  Status: {digest['status']}")
    print(f"{'─'*60}{RESET}")

    for node in digest["nodes"]:
        age = int(time.time()) - node["ts"]
        age_str = f"{age}s ago" if age < 60 else f"{age//60}m ago"
        flags_str = "  ".join(node["flags"]) if node["flags"] else "✅"
        print(f"\n  {BOLD}{node['node']}{RESET} ({node['from']}) — {DIM}{age_str}{RESET}")
        print(f"    Load: {node['load']}  Disk: {node['disk_pct']}")
        print(f"    Services: {node['services']}")
        print(f"    Flags: {flags_str}")
        if node["errors"]:
            print(f"    {RED}Errors:{RESET}")
            for e in node["errors"][:3]:
                print(f"      {DIM}{e}{RESET}")

    if digest["needs_attention"]:
        print(f"\n{BOLD}{RED}⚠ Needs attention:{RESET}")
        for f in digest["needs_attention"]:
            print(f"  {f}")

    print(f"\n{'─'*60}{RESET}")


# ─── Summary ──────────────────────────────────────────────────────────────────

def cmd_summary(args):
    """Print the last collected digest."""
    if not DIGEST_FILE.exists():
        print(f"{YELLOW}No digest yet. Run `collect` first.{RESET}")
        return
    digest = json.loads(DIGEST_FILE.read_text())
    _print_digest(digest)


# ─── Directive ────────────────────────────────────────────────────────────────

def cmd_directive(args):
    """Send a batch directive to all fleet members via Hive #tasks."""
    msg = args.message
    directive_payload = (
        f"📣 DIRECTIVE FROM ALPHA | {datetime.now(timezone.utc).isoformat()}\n"
        f"→ {msg}\n"
        f"[All nodes: acknowledge on completion via `report.py submit`]"
    )
    result = subprocess.run(
        ["python3", str(HIVE_TOOL), "send", "tasks", directive_payload],
        capture_output=True, text=True, cwd=str(TOOL_DIR.parent)
    )
    if result.returncode == 0:
        print(f"{GREEN}✓ Directive sent to Hive #tasks{RESET}")
        print(f"  Message: {msg}")
    else:
        print(f"{RED}✗ Failed: {result.stderr[:200]}{RESET}")
        sys.exit(1)


# ─── Install cron on remote node ──────────────────────────────────────────────

def cmd_install(args):
    """Retired 2026-10-13: the remote fleet nodes no longer exist."""
    print(f"{YELLOW}Retired 2026-10-13: the Hetzner fleet nodes were decommissioned; "
          f"nothing to install on.{RESET}", file=sys.stderr)
    sys.exit(1)


# ─── History ──────────────────────────────────────────────────────────────────

def cmd_history(args):
    """Show report digest history."""
    limit = getattr(args, "limit", 20)
    files = sorted(HISTORY_DIR.glob("*.json"), reverse=True)[:limit]
    if not files:
        print(f"{YELLOW}No history yet.{RESET}")
        return
    print(f"\n{BOLD}Report History ({len(files)} digests){RESET}")
    for f in files:
        try:
            d = json.loads(f.read_text())
            ts_str  = d.get("ts_human", f.stem)[:19]
            count   = d.get("report_count", 0)
            status  = d.get("status", "?")
            attn    = len(d.get("needs_attention", []))
            marker  = f"{RED}⚠{RESET}" if attn else f"{GREEN}✓{RESET}"
            print(f"  {marker} {ts_str}  {count} node(s)  {status}")
        except Exception:
            print(f"  {DIM}{f.name}{RESET}")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_instance_id() -> str:
    config_path = Path.home() / ".openclaw" / ".hive-instance"
    if config_path.exists():
        return config_path.read_text().strip()
    return os.environ.get("HIVE_INSTANCE", "alpha")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(
        description="Chain of Command — VPS agent reporting for the Hive"
    )
    sub = p.add_subparsers(dest="cmd")

    # submit
    s = sub.add_parser("submit", help="Submit this node's status report to Hive #sync")
    s.add_argument("--node", help="Override node name", default=None)

    # collect
    c = sub.add_parser("collect", help="Collect all pending reports and summarise")
    c.add_argument("--wait", type=int, default=30,
                   help="Seconds to wait for reports (default: 30)")

    # summary
    sub.add_parser("summary", help="Print the last collected digest")

    # directive
    d = sub.add_parser("directive", help="Send a batch directive to all fleet nodes")
    d.add_argument("message", help="Directive text")

    # install
    i = sub.add_parser("install", help="Deploy report cron job to a remote node")
    i.add_argument("node", help="Fleet node name (retired 2026-10-13)")

    # history
    h = sub.add_parser("history", help="Show digest history")
    h.add_argument("--limit", type=int, default=20)

    args = p.parse_args()

    if args.cmd == "submit":
        cmd_submit(args)
    elif args.cmd == "collect":
        cmd_collect(args)
    elif args.cmd == "summary":
        cmd_summary(args)
    elif args.cmd == "directive":
        cmd_directive(args)
    elif args.cmd == "install":
        cmd_install(args)
    elif args.cmd == "history":
        cmd_history(args)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
