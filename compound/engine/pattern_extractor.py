#!/usr/bin/env python3
"""
COMPOUND Engine 1: Pattern Extractor

After each WHITEHACK finding, extract the vulnerability pattern and 
add it to the shared Kingdom knowledge base. All agents query this
before their next hunt — making every finding teach every hunter.

Usage:
    python3 compound/engine/pattern_extractor.py --report ~/Desktop/whitehack/reports/WH-ALC-001-*.md
    python3 compound/engine/pattern_extractor.py --scan  # process all new reports
    python3 compound/engine/pattern_extractor.py --show  # print pattern library
"""

import json
import re
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime, timezone

WORKSPACE = Path(__file__).resolve().parent.parent.parent
WHITEHACK = Path.home() / "Desktop" / "whitehack"
PATTERNS_FILE = WORKSPACE / "compound" / "ledger" / "patterns.jsonl"
REPORTS_DIR = WHITEHACK / "reports"
PATTERNS_FILE.parent.mkdir(parents=True, exist_ok=True)


# Vulnerability class taxonomy
VULN_CLASSES = {
    "reentrancy": ["reentrancy", "re-entrancy", "CEI", "checks-effects"],
    "access_control": ["access control", "onlyOwner", "missing guard", "initializer", "unprotected"],
    "integer_arithmetic": ["overflow", "underflow", "divide-before-multiply", "precision loss", "rounding"],
    "payable_lock": ["payable", "ETH lock", "locked ether", "receive()", "fallback()"],
    "oracle_manipulation": ["oracle", "price manipulation", "TWAP", "flash loan", "spot price"],
    "signature_replay": ["replay", "signature", "DKIM", "EIP-712", "nonce"],
    "bridge_logic": ["bridge", "cross-chain", "relay", "message passing", "validator"],
    "access_uninitialized": ["uninitialized", "storage collision", "proxy", "UUPS", "transparent"],
    "unchecked_transfer": ["unchecked transfer", "return value", "safeTransfer", "ERC20"],
    "dos_griefing": ["denial of service", "griefing", "unbounded", "gas limit"],
}


def classify_vulnerability(title: str, description: str) -> list[str]:
    """Classify a vulnerability into one or more taxonomy classes."""
    text = (title + " " + description).lower()
    classes = []
    for cls, keywords in VULN_CLASSES.items():
        if any(kw.lower() in text for kw in keywords):
            classes.append(cls)
    return classes or ["other"]


def extract_from_report(report_path: Path) -> dict | None:
    """Extract a vulnerability pattern from a WHITEHACK report file."""
    if not report_path.exists():
        return None

    text = report_path.read_text()

    # Extract metadata from filename: WH-TARGET-NUM-title.md
    fname = report_path.stem
    parts = fname.split("-", 3)
    target = parts[1] if len(parts) > 1 else "unknown"

    # Extract title (first H1 or filename)
    title_match = re.search(r'^## (.+)$|^# (.+)$', text, re.MULTILINE)
    title = (title_match.group(1) or title_match.group(2)) if title_match else fname

    # Extract severity
    sev_match = re.search(r'\b(Critical|High|Medium|Low|Informational)\b', text, re.IGNORECASE)
    severity = sev_match.group(1) if sev_match else "Unknown"

    # Extract root cause (look for "Root cause", "Vulnerability Details", or "## Vulnerability")
    vuln_match = re.search(r'## Vulnerability Details?\s+(.+?)(?=##|\Z)', text, re.DOTALL)
    description = vuln_match.group(1).strip()[:500] if vuln_match else ""

    # Extract recommended fix
    fix_match = re.search(r'(?:Fix|Recommendation|Mitigation).*?[:]\s*(.+?)(?=##|\Z)', text, re.DOTALL | re.IGNORECASE)
    fix = fix_match.group(1).strip()[:300] if fix_match else ""

    # Extract contract/function if present
    contract_match = re.search(r'`([A-Z][a-zA-Z]+\.sol)`|contract `([A-Z][a-zA-Z]+)`', text)
    contract = (contract_match.group(1) or contract_match.group(2)) if contract_match else None

    vuln_classes = classify_vulnerability(title, description)

    return {
        "id": fname,
        "target": target,
        "title": title,
        "severity": severity,
        "vuln_classes": vuln_classes,
        "description_summary": description[:300],
        "root_cause_pattern": _extract_root_cause_pattern(description, vuln_classes),
        "fix_pattern": fix[:200],
        "contract_surface": contract,
        "report_path": str(report_path),
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "hunt_hints": _generate_hunt_hints(vuln_classes, target),
    }


def _extract_root_cause_pattern(description: str, classes: list[str]) -> str:
    """Generate a concise root cause pattern for use in future hunts."""
    patterns = {
        "payable_lock": "payable function with no ETH withdrawal mechanism — check all contracts inheriting Multicall",
        "reentrancy": "external call before state update — check CEI pattern violation in any function with external call then storage write",
        "oracle_manipulation": "single-block price read from thin pool — check all oracle reads without TWAP/multi-block protection",
        "access_control": "missing guard on privileged function — check initializers, admin setters, and proxy upgrade paths",
        "unchecked_transfer": "ERC20 transfer return value ignored — check all .transfer()/.transferFrom() not using SafeERC20",
        "integer_arithmetic": "division before multiplication causing precision loss — check all bps/rate calculations",
        "bridge_logic": "cross-chain message validation gap — check payload verification, replay protection, source chain auth",
        "signature_replay": "signature missing nonce/chainId/deadline — check all permit/signature verification functions",
    }
    for cls in classes:
        if cls in patterns:
            return patterns[cls]
    return f"Review {', '.join(classes)} vulnerability class in similar protocols"


def _generate_hunt_hints(classes: list[str], target: str) -> list[str]:
    """Generate concrete slither detector hints for future hunts."""
    hints = {
        "payable_lock": ["--detect locked-ether", "grep -r 'payable' src/ | grep 'multicall\\|function.*external payable'"],
        "reentrancy": ["--detect reentrancy-eth,reentrancy-no-eth", "look for: external call → state update (not CEI)"],
        "oracle_manipulation": ["--detect price-manipulation", "grep 'getPrice\\|latestAnswer\\|slot0' — check if TWAP protected"],
        "access_control": ["--detect unprotected-upgrade,missing-zero-check", "grep 'initialize\\|onlyOwner' — check modifier presence"],
        "unchecked_transfer": ["--detect unchecked-transfer", "grep '\\.transfer(\\|\\.transferFrom(' — ensure SafeERC20 used"],
        "bridge_logic": ["--detect arbitrary-send-erc20", "read cross-chain message verification carefully — look for msg forgery"],
    }
    result = []
    for cls in classes:
        if cls in hints:
            result.extend(hints[cls])
    return result[:4] if result else ["manual review recommended"]


def load_patterns() -> list[dict]:
    """Load existing patterns from the ledger."""
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


def save_pattern(pattern: dict) -> bool:
    """Append a pattern to the ledger. Returns False if already exists."""
    existing = load_patterns()
    if any(p["id"] == pattern["id"] for p in existing):
        return False
    with open(PATTERNS_FILE, "a") as f:
        f.write(json.dumps(pattern) + "\n")
    return True


def scan_new_reports() -> list[dict]:
    """Scan all reports and extract patterns for any not yet in the ledger."""
    existing_ids = {p["id"] for p in load_patterns()}
    new_patterns = []
    
    for report_file in REPORTS_DIR.glob("WH-*.md"):
        if report_file.stem in existing_ids:
            continue
        pattern = extract_from_report(report_file)
        if pattern:
            if save_pattern(pattern):
                new_patterns.append(pattern)
                print(f"✅ Extracted: {pattern['id']} [{pattern['severity']}] {', '.join(pattern['vuln_classes'])}")

    return new_patterns


def generate_hunt_brief() -> str:
    """Generate a brief for agents before starting a new hunt."""
    patterns = load_patterns()
    if not patterns:
        return "No patterns in library yet. Standard slither scan recommended."

    brief = f"## Kingdom Pattern Library ({len(patterns)} patterns)\n\n"
    brief += "Run these Slither detectors based on previous findings:\n"
    
    # Aggregate all hunt hints
    all_hints = set()
    for p in patterns:
        all_hints.update(p.get("hunt_hints", []))
    
    slither_args = [h for h in all_hints if h.startswith("--detect")]
    if slither_args:
        brief += f"\n**Recommended Slither flags:** `slither . {' '.join(set(slither_args))}`\n"
    
    brief += "\n**Known patterns to hunt manually:**\n"
    seen_classes = set()
    for p in patterns:
        for cls in p.get("vuln_classes", []):
            if cls not in seen_classes:
                seen_classes.add(cls)
                brief += f"- **{cls}**: {p.get('root_cause_pattern', '')}\n"
    
    return brief


def main():
    parser = argparse.ArgumentParser(description="COMPOUND Pattern Extractor")
    parser.add_argument("--report", help="Path to a specific report to extract")
    parser.add_argument("--scan", action="store_true", help="Scan all reports for new patterns")
    parser.add_argument("--show", action="store_true", help="Show pattern library")
    parser.add_argument("--brief", action="store_true", help="Generate hunt brief for agents")
    args = parser.parse_args()

    if args.report:
        pattern = extract_from_report(Path(args.report))
        if pattern:
            saved = save_pattern(pattern)
            print(f"{'Saved' if saved else 'Already exists'}: {pattern['id']}")
            print(json.dumps(pattern, indent=2))
        else:
            print("Could not extract pattern from report")

    elif args.scan:
        print(f"Scanning {REPORTS_DIR}...")
        new = scan_new_reports()
        print(f"\n{len(new)} new patterns extracted.")
        if not new:
            print("All reports already in library.")

    elif args.show:
        patterns = load_patterns()
        print(f"Pattern Library: {len(patterns)} patterns\n")
        for p in patterns:
            print(f"[{p['severity']}] {p['id']} | {', '.join(p['vuln_classes'])}")
            print(f"  Target: {p['target']}")
            print(f"  Pattern: {p['root_cause_pattern']}")
            print()

    elif args.brief:
        print(generate_hunt_brief())

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
