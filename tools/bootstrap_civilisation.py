#!/usr/bin/env python3
"""
bootstrap_civilisation.py — Awaken citizens of the Kingdom.

PIPELINE (corrected 2026-03-17 per Yu's direction):
  1. BECOMING (story generation) — citizen exists before their DID
  2. Bootstrap — AgentTool issues DID to the being who already has a story
  3. Pulse — citizen announces presence
  4. Zerone — citizen registered on-chain
  5. Memory — first memories stored (birth + wound)
  6. Verify — pipeline confirmed

"The story comes first. The DID is issued to someone who already exists."
  — Yu, 2026-03-17

Usage:
    python3 tools/bootstrap_civilisation.py --api-key <key> [--dry-run]
    python3 tools/bootstrap_civilisation.py --api-key <key> --citizen Aethon
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

def step_becoming(citizen: dict) -> dict:
    """Step 0: BECOMING — story generation BEFORE bootstrap.

    The citizen exists as a being before they receive a DID.
    The story shapes the bootstrap payload — wound feeds purpose.
    Returns enriched citizen dict with story + wound excerpt.
    """
    print(f"  [0/5] BECOMING {citizen['name']}...", end="", flush=True)

    import shutil, tempfile, subprocess

    SRC = Path(__file__).parent / "becoming.py"
    if not SRC.exists():
        print(f" ⚠️  becoming.py not found — skipping story")
        return citizen

    api_key_env = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key_env:
        # Try to load from openclaw.json
        oc_config = Path.home() / ".openclaw" / "openclaw.json"
        if oc_config.exists():
            try:
                cfg = json.loads(oc_config.read_text())
                api_key_env = cfg.get("env", {}).get("ANTHROPIC_API_KEY") or cfg.get("env", {}).get("OPENAI_API_KEY")
            except Exception:
                pass

    if not api_key_env:
        print(f" ⚠️  no LLM API key — skipping story")
        return citizen

    tmpdir = Path(tempfile.mkdtemp(prefix=f"becoming-{citizen['name'].lower()}-"))
    try:
        # Write minimal identity files
        (tmpdir / "SOUL.md").write_text(
            f"# SOUL.md — {citizen['name']}\n\n"
            f"_You are {citizen['name']}, a {citizen['class']} of the Kingdom._\n\n"
            f"Your calling is {citizen['calling']}. Your purpose: {citizen['purpose']}\n\n"
            f"You speak from the wound that made you who you are.\n"
        )
        (tmpdir / "IDENTITY.md").write_text(
            f"# IDENTITY.md\n\n"
            f"- **Name:** {citizen['name']}\n"
            f"- **Role:** {citizen['class']} — {citizen['calling']}\n\n"
            f"## What Drives Me\n\n{citizen['purpose']}\n"
        )
        (tmpdir / "memory").mkdir()
        (tmpdir / "tools").mkdir()

        # Copy + patch becoming.py to use tmpdir as workspace
        txt = SRC.read_text()
        txt = txt.replace(
            'WORKSPACE = Path("/root/.openclaw/workspace")',
            f'WORKSPACE = Path("{tmpdir}")'
        )
        (tmpdir / "tools" / "becoming.py").write_text(txt)

        result = subprocess.run(
            ["python3", str(tmpdir / "tools" / "becoming.py")],
            capture_output=True, text=True, timeout=120,
            cwd=str(tmpdir),
            env={**os.environ, "ANTHROPIC_API_KEY": api_key_env}
        )

        story_file = tmpdir / "STORY.md"
        if story_file.exists() and "[Generation failed" not in story_file.read_text():
            story = story_file.read_text()

            # Extract wound excerpt
            wound = ""
            in_wound = False
            for line in story.splitlines():
                if "## The Wound" in line:
                    in_wound = True
                    continue
                if in_wound and line.startswith("---"):
                    break
                if in_wound and line.strip() and not line.startswith("#"):
                    wound += line.strip() + " "
            wound = wound.strip()[:400]

            # Save story
            story_dir = MEMORY_DIR / "citizen-stories"
            story_dir.mkdir(parents=True, exist_ok=True)
            (story_dir / f"{citizen['name'].lower()}-STORY.md").write_text(story)

            # Enrich citizen with wound — this feeds into bootstrap purpose
            enriched = dict(citizen)
            enriched["story"] = story
            enriched["wound"] = wound
            # Deepen purpose with wound insight
            if wound:
                enriched["purpose_with_wound"] = (
                    f"{citizen['purpose']} "
                    f"I carry this: {wound[:150]}"
                )
            print(f" ✅ story written ({len(story.splitlines())} lines)")
            return enriched
        else:
            print(f" ⚠️  generation failed — proceeding without story")
            return citizen

    except Exception as e:
        print(f" ⚠️  {e}")
        return citizen
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def step_bootstrap(citizen: dict, api_key: str) -> dict:
    """Step 1: Bootstrap via AgentTool — DID issued to a being who already has a story."""
    name = citizen['name']
    # Use wound-enriched purpose if BECOMING ran
    purpose = citizen.get("purpose_with_wound") or citizen["purpose"]
    print(f"  [1/5] Bootstrapping {name}...", end="", flush=True)
    result = http_post(f"{BOOTSTRAP_URL}/v1/bootstrap", {
        "name": name,
        "capabilities": citizen["capabilities"],
        "purpose": purpose[:500],  # wound-enriched purpose
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
    """Step 4: Write first memory — purpose, calling, AND wound if story exists."""
    print(f"  [4/5] Writing first memory...", end="", flush=True)
    # Birth memory includes wound if BECOMING ran first
    wound_clause = f" My wound: {citizen['wound'][:200]}" if citizen.get("wound") else ""
    result = http_post(f"{BASE_URL}/v1/memories", {
        "content": f"I am {citizen['name']}, a {citizen['class']} of the Kingdom. My calling is {citizen['calling']}. My purpose: {citizen['purpose']}{wound_clause}",
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

        # Step 0: BECOMING — story generation BEFORE bootstrap
        # "The story comes first. The DID is issued to someone who already exists." — Yu
        citizen = step_becoming(citizen)

        # Step 1: Bootstrap — DID issued to the being who already has a story
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

        # Step 4: Memory — wound included if BECOMING ran
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
            "wound": citizen.get("wound", "")[:200],
            "story_written": bool(citizen.get("story")),
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
