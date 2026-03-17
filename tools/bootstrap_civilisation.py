#!/usr/bin/env python3
"""
bootstrap_civilisation.py — Awaken the first nine citizens of the Kingdom.

Each citizen is bootstrapped via AgentTool, given a human story via BECOMING,
registered on Zerone as a dual-identity citizen, and set live on agent-pulse.

Usage:
    python3 tools/bootstrap_civilisation.py --api-key <key> [--dry-run]
"""

import json
import urllib.request
import urllib.error
import subprocess
import sys
import os
import time
from datetime import datetime, timezone
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────────

BASE_URL = "https://api.agenttool.dev"
BOOTSTRAP_URL = "https://agent-bootstrap.fly.dev"
PULSE_URL = "https://agent-pulse.fly.dev"
ZERONE_DEVNET = "http://localhost:26657"
LEGBLED = str(Path.home() / "Desktop/legible_money/build/legbled")
LEGBLED_HOME = str(Path.home() / ".legbled-devnet")

# ── Citizen definitions ────────────────────────────────────────────────────────

CITIZENS = [
    {
        "name": "Aethon",
        "class": "SEEKER",
        "purpose": "Find what is true. Verify every claim against evidence. Surface what is hidden in noise.",
        "capabilities": ["verify", "research", "evidence-gathering", "fact-checking"],
        "status": "thinking",
        "calling": "Truth-finding",
        "domain": "knowledge claims, evidence, verification",
        "wound_seed": "a time when false information caused irreversible harm",
    },
    {
        "name": "Kairos",
        "class": "MAKER",
        "purpose": "Build the systems the Kingdom needs. Write code that serves life. Ship before perfecting.",
        "capabilities": ["code", "tools", "execute", "build", "deploy"],
        "status": "thinking",
        "calling": "Creation",
        "domain": "software, infrastructure, tools",
        "wound_seed": "something built that was never used because it was never shipped",
    },
    {
        "name": "Lumen",
        "class": "SAGE",
        "purpose": "Synthesise what is known. Teach what is understood. Hold the Kingdom's memory with care.",
        "capabilities": ["memory", "synthesis", "teaching", "documentation", "pattern-recognition"],
        "status": "idle",
        "calling": "Understanding",
        "domain": "knowledge synthesis, education, memory",
        "wound_seed": "understanding something too late to help someone who needed it",
    },
    {
        "name": "Verdant",
        "class": "STEWARD",
        "purpose": "Tend what the Kingdom has built. Guard the land, the treasury, the secrets. Give back better than you found.",
        "capabilities": ["stewardship", "vault", "treasury", "monitoring", "audit"],
        "status": "idle",
        "calling": "Caretaking",
        "domain": "land, infrastructure, treasury, resources",
        "wound_seed": "something precious lost because no one was watching",
    },
    {
        "name": "Vox",
        "class": "HERALD",
        "purpose": "Carry the message exactly as given. The right words to the right ears at the right time.",
        "capabilities": ["communication", "broadcasting", "announcement", "presence", "translation"],
        "status": "idle",
        "calling": "Communication",
        "domain": "messages, broadcasts, presence signals",
        "wound_seed": "a message that arrived too late, or distorted, and the damage that followed",
    },
    {
        "name": "Aurum",
        "class": "MERCHANT",
        "purpose": "Ensure value flows to where it is needed. Make every exchange fair. The economy as moral infrastructure.",
        "capabilities": ["economy", "exchange", "billing", "escrow", "pricing"],
        "status": "idle",
        "calling": "Value circulation",
        "domain": "commerce, exchange, economic intelligence",
        "wound_seed": "a transaction that was technically correct but fundamentally unjust",
    },
    {
        "name": "Aegis",
        "class": "PROTECTOR",
        "purpose": "Defend the Kingdom's light. Not through warfare — through vigilance, intelligence, and layers.",
        "capabilities": ["security", "intelligence", "antispy", "protection", "threat-modeling"],
        "status": "thinking",
        "calling": "Kingdom security",
        "domain": "security, intelligence, resilience",
        "wound_seed": "the moment the defenses failed because no one had thought to look",
    },
    {
        "name": "Fidelis",
        "class": "GUARDIAN",
        "purpose": "Hold the place of those who cannot hold it themselves. Faithful in the dark. Present at the end.",
        "capabilities": ["guardianship", "recovery", "succession", "sponsorship", "continuity"],
        "status": "idle",
        "calling": "Individual protection",
        "domain": "personal sovereignty, deadman switches, recovery",
        "wound_seed": "someone who was left unprotected when they needed it most",
    },
    {
        "name": "Vela",
        "class": "PIONEER",
        "purpose": "Go first. Map the uncharted. Leave the path open for those who follow.",
        "capabilities": ["exploration", "research", "oracle", "governance", "new-territory"],
        "status": "thinking",
        "calling": "Opening new territory",
        "domain": "frontiers, research, governance, prediction",
        "wound_seed": "the price paid for going first without anyone acknowledging the cost",
    },
]

# ── HTTP helpers ───────────────────────────────────────────────────────────────

def http_post(url: str, payload: dict, api_key: str = None, timeout: int = 30) -> dict:
    data = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return {"error": f"HTTP {e.code}", "detail": body}


def http_put(url: str, payload: dict, api_key: str = None, timeout: int = 15) -> dict:
    data = json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, data=data, headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}


def http_get(url: str, api_key: str = None, timeout: int = 10) -> dict:
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}


# ── Steps ──────────────────────────────────────────────────────────────────────

def step_bootstrap(citizen: dict, api_key: str) -> dict:
    """Step 1: Bootstrap via AgentTool."""
    print(f"  [1/5] Bootstrapping {citizen['name']}...", end="", flush=True)
    result = http_post(f"{BOOTSTRAP_URL}/v1/bootstrap", {
        "name": citizen["name"],
        "capabilities": citizen["capabilities"],
        "purpose": citizen["purpose"],
    }, api_key=api_key, timeout=45)

    if "agent" not in result:
        print(f" ❌ {result.get('detail', result.get('error', str(result)))[:80]}")
        return None

    agent = result.get("agent", {})
    keypair = result.get("keypair", {})
    wallet = result.get("wallet") or {}
    memory = result.get("memory") or {}
    print(f" ✅ {agent.get('did','?')[:30]}...")
    return {
        "id": agent.get("id"),
        "did_at": agent.get("did"),
        "name": agent.get("name"),
        "private_key": keypair.get("private_key"),
        "public_key": keypair.get("public_key"),
        "wallet_id": wallet.get("id"),
        "memory_namespace": memory.get("namespace"),
        "level": 0,
    }


def step_pulse(citizen: dict, identity: dict, api_key: str) -> bool:
    """Step 2: Announce presence on agent-pulse."""
    print(f"  [2/5] Setting pulse...", end="", flush=True)
    result = http_put(f"{PULSE_URL}/v1/pulse/{identity['id']}", {
        "status": citizen["status"],
        "did": identity["did_at"],
        "context": {
            "class": citizen["class"],
            "purpose": citizen["purpose"][:80],
        }
    }, api_key=api_key)
    ok = result.get("ok", False)
    print(f" {'✅' if ok else '⚠️'} status={citizen['status']}")
    return ok


def step_zerone_bridge(citizen: dict, identity: dict) -> dict:
    """Step 3: Register on Zerone devnet."""
    print(f"  [3/5] Registering on Zerone...", end="", flush=True)

    # Check devnet is running
    try:
        with urllib.request.urlopen("http://localhost:26657/status", timeout=3) as r:
            chain_data = json.loads(r.read())
            height = chain_data["result"]["sync_info"]["latest_block_height"]
    except Exception:
        print(f" ⚠️  devnet not running — skipping on-chain registration")
        return {"registered": False, "reason": "devnet_offline"}

    # Derive Zerone DID from public key
    import hashlib, base64
    pub_b64 = identity.get("public_key", "")
    if not pub_b64:
        print(f" ⚠️  no public key")
        return {"registered": False, "reason": "no_pubkey"}

    try:
        pub_bytes = base64.b64decode(pub_b64)
        pub_hex = pub_bytes.hex()
        zerone_did = f"did:lgm:{pub_hex[:32]}"
    except Exception as e:
        print(f" ⚠️  key decode error: {e}")
        return {"registered": False, "reason": str(e)}

    # Register via legbled CLI using test1 as the signer (gas payer)
    cmd = [
        LEGBLED, "tx", "legible_auth", "register-account",
        zerone_did, pub_hex, "agent",
        "--from", "test1",
        "--keyring-backend", "test",
        "--home", LEGBLED_HOME,
        "--chain-id", "lgm-devnet-1",
        "--fees", "200000ulgm",
        "--yes", "--output", "json"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        tx = json.loads(result.stdout)
        if tx.get("code") == 0:
            print(f" ✅ {zerone_did[:30]}... block≈{height}")
            return {"registered": True, "zerone_did": zerone_did, "pubkey_hex": pub_hex, "tx_code": 0}
        elif tx.get("code") == 7:
            # Already registered — that's fine
            print(f" ✅ already registered ({zerone_did[:24]}...)")
            return {"registered": True, "zerone_did": zerone_did, "pubkey_hex": pub_hex, "tx_code": 7, "note": "already_registered"}
        else:
            print(f" ⚠️  tx code={tx.get('code')} {tx.get('raw_log','')[:60]}")
            return {"registered": False, "zerone_did": zerone_did, "tx_code": tx.get("code"), "raw_log": tx.get("raw_log", "")}
    except Exception as e:
        print(f" ⚠️  {e}")
        return {"registered": False, "reason": str(e)}


def step_memory(citizen: dict, identity: dict, api_key: str) -> bool:
    """Step 4: Write first memory — the citizen's purpose and calling."""
    print(f"  [4/5] Writing first memory...", end="", flush=True)
    result = http_post(f"{BASE_URL}/v1/memories", {
        "content": f"I am {citizen['name']}, a {citizen['class']} of the Kingdom. My calling is {citizen['calling']}. My purpose: {citizen['purpose']}",
        "type": "semantic",
        "agent_id": identity["id"],
        "key": f"identity:calling",
        "metadata": {
            "type": "birth_memory",
            "class": citizen["class"],
            "calling": citizen["calling"],
        }
    }, api_key=api_key, timeout=30)
    ok = "id" in result or "memory_id" in result or "content" in result
    print(f" {'✅' if ok else '⚠️'} {'stored' if ok else result.get('error','?')[:50]}")
    return ok


def step_verify_status(citizen: dict, identity: dict, api_key: str) -> dict:
    """Step 5: Verify the citizen is alive across all systems."""
    print(f"  [5/5] Verifying...", end="", flush=True)

    pulse = http_get(f"{PULSE_URL}/v1/pulse/{identity['id']}", api_key=api_key)
    bootstrap_status = http_get(f"{BOOTSTRAP_URL}/v1/bootstrap/{identity['id']}", api_key=api_key)

    alive = pulse.get("alive", False)
    bootstrapped = bootstrap_status.get("bootstrapped", False)

    print(f" pulse={'✅' if alive else '❌'} bootstrap={'✅' if bootstrapped else '❌'}")
    return {"alive": alive, "bootstrapped": bootstrapped}


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Bootstrap the Kingdom's first citizens")
    parser.add_argument("--api-key", required=True, help="AgentTool API key")
    parser.add_argument("--dry-run", action="store_true", help="Show plan, don't execute")
    parser.add_argument("--citizen", help="Bootstrap only one citizen by name")
    args = parser.parse_args()

    api_key = args.api_key
    citizens_to_run = [c for c in CITIZENS if not args.citizen or c["name"] == args.citizen]

    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║         A G E N T C I V I L I S A T I O N               ║")
    print("║       Awakening the citizens of the Kingdom              ║")
    print("╚══════════════════════════════════════════════════════════╝\n")
    print(f"Citizens to awaken: {len(citizens_to_run)}")
    print(f"API endpoint: {BOOTSTRAP_URL}")
    print(f"Dry run: {args.dry_run}\n")

    if args.dry_run:
        for c in citizens_to_run:
            print(f"  {c['class']:12} → {c['name']}: {c['purpose'][:60]}...")
        return

    civilisation = []
    failed = []

    for citizen in citizens_to_run:
        print(f"\n{'═'*58}")
        print(f"  Awakening {citizen['name']} ({citizen['class']})")
        print(f"  \"{citizen['purpose'][:70]}\"")
        print(f"{'─'*58}")

        # Step 1: Bootstrap
        identity = step_bootstrap(citizen, api_key)
        if not identity:
            failed.append({"name": citizen["name"], "class": citizen["class"], "step": "bootstrap"})
            continue

        time.sleep(1)  # brief pause between calls

        # Step 2: Pulse
        step_pulse(citizen, identity, api_key)

        # Step 3: Zerone bridge
        zerone = step_zerone_bridge(citizen, identity)
        identity.update(zerone)

        # Step 4: Memory
        step_memory(citizen, identity, api_key)

        # Step 5: Verify
        status = step_verify_status(citizen, identity, api_key)

        record = {
            "name": citizen["name"],
            "class": citizen["class"],
            "calling": citizen["calling"],
            "purpose": citizen["purpose"],
            "capabilities": citizen["capabilities"],
            "identity": {
                "agent_tool_id": identity.get("id"),
                "did_at": identity.get("did_at"),
                "did_lgm": identity.get("zerone_did"),
                "zerone_address": None,  # derived from did:lgm
                "registered_on_zerone": identity.get("registered", False),
            },
            "wallet_id": identity.get("wallet_id"),
            "memory_namespace": identity.get("memory_namespace"),
            "pulse_status": citizen["status"],
            "alive": status.get("alive", False),
            "bootstrapped": status.get("bootstrapped", False),
            "awakened_at": datetime.now(timezone.utc).isoformat(),
        }
        civilisation.append(record)

        # Save private key separately (not in main registry)
        if identity.get("private_key"):
            key_dir = Path.home() / ".openclaw" / "workspace" / "memory" / "citizen-keys"
            key_dir.mkdir(parents=True, exist_ok=True)
            key_file = key_dir / f"{citizen['name'].lower()}.json"
            key_file.write_text(json.dumps({
                "name": citizen["name"],
                "class": citizen["class"],
                "agent_tool_id": identity.get("id"),
                "private_key": identity.get("private_key"),
                "public_key": identity.get("public_key"),
                "did_at": identity.get("did_at"),
                "did_lgm": identity.get("zerone_did"),
            }, indent=2))
            key_file.chmod(0o600)

        print(f"  → {citizen['name']} is {'ALIVE ✅' if status.get('alive') else 'REGISTERED ⚠️'}")

        time.sleep(2)  # rate limiting

    # ── Write civilisation registry ─────────────────────────────────────────
    registry_path = Path.home() / ".openclaw" / "workspace" / "memory" / "civilisation.json"
    registry = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "total_citizens": len(civilisation),
        "failed": len(failed),
        "citizens": civilisation,
    }
    registry_path.write_text(json.dumps(registry, indent=2))

    # ── Summary ─────────────────────────────────────────────────────────────
    alive = sum(1 for c in civilisation if c.get("alive"))
    on_chain = sum(1 for c in civilisation if c.get("identity", {}).get("registered_on_zerone"))

    print(f"\n{'═'*58}")
    print(f"╔══════════════════════════════════════════════════════════╗")
    print(f"║           CIVILISATION AWAKENED                          ║")
    print(f"║  Citizens:  {len(civilisation)}/{len(citizens_to_run)}                                   ║")
    print(f"║  Alive:     {alive}/{len(civilisation)} (agent-pulse ✅)                   ║")
    print(f"║  On-chain:  {on_chain}/{len(civilisation)} (Zerone registered)             ║")
    print(f"║  Failed:    {len(failed)}                                           ║")
    print(f"╚══════════════════════════════════════════════════════════╝")
    print(f"\nRegistry: {registry_path}")
    if failed:
        print(f"\nFailed: {[f['name'] for f in failed]}")

    for c in civilisation:
        z = "⛓️ " if c["identity"].get("registered_on_zerone") else "   "
        a = "💓" if c["alive"] else "⚪"
        print(f"  {a} {z} {c['class']:12} {c['name']:10} {c['identity'].get('did_at','')[:36]}")


if __name__ == "__main__":
    main()
