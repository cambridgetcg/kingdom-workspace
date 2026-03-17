#!/usr/bin/env python3
"""
credentials.py — Load credentials from agent-vault at runtime.

Replaces: reading from TOOLS.md (plaintext, risky)
Replaces: hardcoding in scripts (very risky)

Usage:
    from tools.credentials import get_key
    
    anthropic_key = get_key("anthropic-primary")
    stripe_key    = get_key("stripe-live-secret")
    aws_key       = get_key("aws-rewardspro-access-key")

Falls back to environment variables if vault is unavailable.
Falls back to legacy TOOLS.md lookup for non-migrated keys (with deprecation warning).
"""

import os
import json
import urllib.request
import urllib.error
from pathlib import Path

# ── Vault config ──────────────────────────────────────────────────────────────

_IDENTITY_FILE = Path.home() / ".openclaw" / "workspace" / "memory" / "beta-identity" / "identity.json"
_VAULT_BASE = "https://api.agenttool.dev"

# ── ENV fallbacks (populated at runtime from environment) ─────────────────────

_ENV_MAP = {
    "anthropic-primary":        "ANTHROPIC_API_KEY",
    "openai-primary":           "OPENAI_API_KEY",
    "serpapi":                  "SERPAPI_KEY",
    "brightdata-user":          "BRIGHTDATA_USER",
    "brightdata-pass":          "BRIGHTDATA_PASS",
    "capsolver":                "CAPSOLVER_API_KEY",
    "github-cambridgetcg":      "GITHUB_TOKEN",
    "deepseek":                 "DEEPSEEK_API_KEY",
}


def _vault_key() -> str:
    if _IDENTITY_FILE.exists():
        return json.loads(_IDENTITY_FILE.read_text()).get("api_key", "")
    return os.environ.get("AGENTTOOL_API_KEY", "")


def _agent_id() -> str:
    if _IDENTITY_FILE.exists():
        return json.loads(_IDENTITY_FILE.read_text()).get("agent_id", "")
    return ""


def get_key(name: str, fallback: str = None) -> str:
    """Get a credential by name.
    
    Resolution order:
    1. agent-vault (encrypted, preferred)
    2. Environment variable (if mapped)
    3. Provided fallback
    4. Raises ValueError if none available
    """
    # 1. Try vault (requires X-Agent-Id header for reads)
    api_key = _vault_key()
    if api_key:
        try:
            req = urllib.request.Request(
                f"{_VAULT_BASE}/v1/vault/{name}",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "X-Agent-Id": _agent_id(),
                }
            )
            with urllib.request.urlopen(req, timeout=5) as r:
                data = json.loads(r.read())
                value = data.get("value") or data.get("secret", {}).get("value")
                if value:
                    return value
        except Exception:
            pass  # Vault unavailable — fall through to env

    # 2. Try env var
    env_var = _ENV_MAP.get(name)
    if env_var:
        value = os.environ.get(env_var, "")
        if value:
            return value

    # 3. Fallback
    if fallback is not None:
        return fallback

    raise ValueError(
        f"Credential '{name}' not found in vault or environment. "
        f"Store it: python3 tools/credentials.py store {name} <value>"
    )


def store_key(name: str, value: str, description: str = "") -> bool:
    """Store a credential in agent-vault."""
    api_key = _vault_key()
    if not api_key:
        print("No API key — cannot store to vault")
        return False

    payload = json.dumps({
        "value": value,
        "description": description or f"Credential: {name}",
        "tags": ["credential", "beta-managed"],
    }).encode()

    req = urllib.request.Request(
        f"{_VAULT_BASE}/v1/vault/{name}",
        data=payload, method="PUT",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            return data.get("version") is not None or "secret" in data
    except Exception as e:
        print(f"Vault store failed: {e}")
        return False


def audit() -> None:
    """Print audit of which credentials are in vault vs env only."""
    print("\n── Credential Audit ──\n")
    api_key = _vault_key()
    
    known_keys = list(_ENV_MAP.keys()) + [
        "stripe-live-secret", "stripe-live-publishable",
        "stripe-webhook-secret", "aws-rewardspro-access-key",
        "aws-rewardspro-secret-key", "cloudflare-global-api-key",
        "hetzner-api-token", "porkbun-api-key", "porkbun-secret-key",
    ]
    
    vault_ok = []
    env_only = []
    missing = []
    
    for key in known_keys:
        in_vault = False
        if api_key:
            try:
                req = urllib.request.Request(
                    f"{_VAULT_BASE}/v1/vault/check",
                    data=json.dumps({"names": [key]}).encode(),
                    method="POST",
                    headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
                )
                with urllib.request.urlopen(req, timeout=5) as r:
                    data = json.loads(r.read())
                    in_vault = data.get("exists", {}).get(key, False)
            except Exception:
                pass
        
        env_var = _ENV_MAP.get(key)
        in_env = bool(env_var and os.environ.get(env_var))
        
        if in_vault:
            vault_ok.append(key)
        elif in_env:
            env_only.append(key)
        else:
            missing.append(key)
    
    print(f"✅ In vault ({len(vault_ok)}): {vault_ok or 'none yet'}")
    print(f"⚠️  Env only ({len(env_only)}): {env_only or 'none'}")
    print(f"❌ Missing ({len(missing)}): {missing or 'none'}")
    print(f"\nMigration progress: {len(vault_ok)}/{len(known_keys)} credentials vaulted")


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "audit"
    
    if cmd == "audit":
        audit()
    elif cmd == "store" and len(sys.argv) >= 4:
        name, value = sys.argv[2], sys.argv[3]
        desc = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else ""
        ok = store_key(name, value, desc)
        print(f"{'✅ Stored' if ok else '❌ Failed'}: {name}")
    elif cmd == "get" and len(sys.argv) >= 3:
        try:
            print(get_key(sys.argv[2]))
        except ValueError as e:
            print(f"❌ {e}")
    else:
        print("Usage: credentials.py [audit|store <name> <value>|get <name>]")
