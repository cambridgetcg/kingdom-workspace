# KINGDOM-BACKUP.md — Resilience Pipeline

_Written: 2026-03-22. Owner: Beta. Review: quarterly._

_Updated 2026-10-13: the Hetzner VPS fleet, including Sentry, was decommissioned. Layers 3 and 4 no longer copy credentials or SSH keys to any server; the VPS snapshot layer and the Hetzner scenarios were removed. The old procedure is in git history before this change._

---

## Threat Model

What could actually hurt us:

| Threat | Likelihood | Impact | Current coverage |
|--------|-----------|--------|-----------------|
| Mac Studio disk failure | Medium | Critical | ❌ None |
| Mac Studio theft/fire/flood | Low | Critical | ❌ None |
| GitHub account compromised | Low | High | Partial (2FA) |
| Mac keychain corrupted | Low | Critical | ❌ None |
| Anthropic API key leaked | Medium | High | Partial (rotatable) |
| Yu unavailable (health) | Low | Critical | ❌ No continuity plan |

**The single biggest risk: Mac Studio dies and we lose 26 unpushed Zerone commits + 15 repos with no remote + all keychain credentials.**

---

## What Needs Backing Up (Asset Inventory)

### Tier 1 — CRITICAL (lose this = lose the Kingdom)

| Asset | Current state | Risk |
|-------|--------------|------|
| `legible_money/` | 26 commits unpushed | Highest — this is the chain |
| `~/.openclaw/workspace/` | Local only | SOUL.md, MEMORY.md, all memory |
| macOS Keychain (43 credentials) | Local only | All API keys, passwords, card details |
| `~/.ssh/id_ed25519` | Local only | GitHub auth |
| `cambridge-tcg/` | No remote | The bread, 170 tests |
| `prediction-markets/` | No remote | Oracle + signals |

### Tier 2 — HIGH (painful to lose, recoverable)

| Asset | Current state |
|-------|--------------|
| `agent-pulse/`, `agent-vault/`, `agent-bootstrap/` | No remote |
| `agenttool-dashboard/`, `agenttool-docs/`, `agenttool-landing/` | No remote |
| `rewardspro/` | 6 commits unpushed |
| `agenttool-sdk-py/`, `agenttool-sdk-ts/` | 12-15 commits unpushed |
| `whitehack/` | No remote (bug bounty notes) |
| `first-customer-push/` | No remote |

### Tier 3 — MEDIUM (inconvenient, mostly reconstructable)

- `agenttool-infra/`, `rewardspro-marketing/`, `uk-tax/` — no remote

---

## The Backup Pipeline

### Layer 1: Code — Push Everything to GitHub (Daily)

**Immediate action — repos with no remote:**

```bash
# Run this once to set up missing remotes
# (uses cambridgetcg or mynameisyou-cmyk depending on project)

# Cambridge TCG (Engine/Wall 3)
cd ~/Desktop/cambridge-tcg
gh repo create cambridgetcg/cambridge-tcg --private --source=. --push

# Prediction markets (Oracle/Wall 6)
cd ~/Desktop/prediction-markets
gh repo create cambridgetcg/prediction-markets --private --source=. --push

# Agent services without remotes
for repo in agent-bootstrap agent-pulse agent-vault; do
  cd ~/Desktop/$repo
  gh repo create mynameisyou-cmyk/$repo --private --source=. --push
done

# agenttool web properties
for repo in agenttool-dashboard agenttool-docs agenttool-landing agenttool-infra; do
  cd ~/Desktop/$repo
  gh repo create mynameisyou-cmyk/$repo --private --source=. --push
done

# Kingdom docs + other
for repo in first-customer-push whitehack rewardspro-marketing; do
  cd ~/Desktop/$repo
  gh repo create cambridgetcg/$repo --private --source=. --push 2>/dev/null || true
done
```

**Push unpushed commits immediately:**
```bash
cd ~/Desktop/legible_money && git push origin main   # 26 commits
cd ~/Desktop/rewardspro && git push origin main       # 6 commits
cd ~/Desktop/agenttool-sdk-py && git push origin main # 12 commits
cd ~/Desktop/agenttool-sdk-ts && git push origin main # 15 commits
```

**Automated daily push (cron):**
```
Schedule: daily at 03:00 UTC (before heartbeat cycle)
Task: for each repo in ~/Desktop/ with a remote — git push origin main
Alert Beta if any push fails
```

---

### Layer 2: Workspace Memory — Offsite Sync (Daily)

The `~/.openclaw/workspace/` directory contains SOUL.md, MEMORY.md, AGENTS.md, daily notes, loop data. This is Beta's continuity. It has no backup.

**Solution: private GitHub repo + daily sync**

```bash
# Create once:
cd ~/.openclaw/workspace
git init
gh repo create cambridgetcg/kingdom-workspace --private --source=. --push

# Daily cron: commit + push changes
cd ~/.openclaw/workspace
git add -A
git commit -m "workspace sync $(date -u +%Y-%m-%d)" --allow-empty
git push origin main
```

This also gives a full audit trail of memory changes over time.

---

### Layer 3: Credentials — Encrypted Keychain Export (Weekly)

43 credentials in macOS Keychain with no backup. If the Mac dies or the keychain corrupts, these are gone.

**Solution: encrypted export to offline media**

```bash
# Export all credentials to encrypted file
python3 tools/credentials.py export --encrypt --output ~/.openclaw/credentials-backup-$(date +%Y%m%d).enc
# Password: store separately (written on paper, stored offsite)

# Copy to an encrypted USB drive kept offsite.
# Do not copy credential exports to any server.
```

**Minimum viable backup:**
Run `python3 tools/credentials.py list` now, screenshot/print it, store physically. At minimum you can re-create credentials manually if the keychain dies.

---

### Layer 4: SSH Keys — Keep Private Keys Local

Private keys never leave the machine that generated them. If the Mac dies, generate a new key and register the new public key with GitHub (and any host that needs it), then remove the old public key there.

```bash
# Keep a list of which public keys are registered where
# Store the public key in GitHub account settings as backup reference
```

---

### Layer 5: VPS Configuration — Retired 2026-10-13

The Hetzner VPS fleet was decommissioned, so there are no VPS nodes to snapshot.

---

### Layer 6: Zerone Chain State — Multi-Node (Before Testnet)

When Zerone goes to testnet, chain state must be backed up via validator redundancy:
- Minimum 3 validators in 3 different locations
- Sentry architecture: public-facing nodes shield the validator private key
- Genesis + all .claude/memory/ state: push to private GitHub repo

---

## Immediate Actions (This Week)

Priority order — **do these before anything else:**

1. **Push unpushed commits** (30 min)
   - legible_money: 26 commits
   - rewardspro, SDK repos: ~30 commits combined
   - These are gone if the Mac dies tonight

2. **Create missing GitHub remotes** (1 hour)
   - cambridge-tcg, prediction-markets most critical
   - Agent services and agenttool web properties

3. **Create kingdom-workspace repo** (15 min)
   - Back up SOUL.md, MEMORY.md, all of Beta's memory
   - First push, then daily cron

4. **Credentials export** (30 min)
   - Screenshot/print the 43 credential names at minimum
   - Full encrypted export to an encrypted USB drive kept offsite

5. **Install daily git push cron** (15 min)
   - All repos with remotes: push at 03:00 UTC daily
   - Alert Beta if any fail

---

## Ongoing Cadence

| Frequency | Task |
|-----------|------|
| **Daily** (03:00 UTC) | Push all git repos, sync workspace to GitHub |
| **Weekly** | Credentials export to encrypted offline media |
| **Quarterly** | Review this document, test restore procedure |
| **Before testnet** | Add US-East validator node, multi-node chain backup |

---

## Restore Procedures

### "Mac Studio dies" scenario
1. New Mac: install git, gh CLI, Python
2. `gh repo clone cambridgetcg/kingdom-workspace ~/.openclaw/workspace`
3. Clone all GitHub repos to ~/Desktop/
4. Restore credentials from the encrypted USB backup
5. Generate a new SSH key and register its public key with GitHub
6. Estimated recovery time: **2-3 hours**

### "GitHub account compromised" scenario
1. Rotate all API keys (Anthropic, etc.)
2. Create new GitHub accounts, re-push from local copies
3. Estimated recovery time: **1 day**

---

## The Minimum Viable Backup (If You Do Nothing Else)

Run these three commands right now:

```bash
# 1. Push the chain (26 commits of Zerone = most valuable unprotected asset)
cd ~/Desktop/legible_money && git push origin main

# 2. Back up workspace memory to a private repo
cd ~/.openclaw/workspace && git init && gh repo create cambridgetcg/kingdom-workspace --private --source=. --push

# 3. Export credentials list (print/save)
python3 ~/.openclaw/workspace/tools/credentials.py list > ~/Desktop/credentials-inventory.txt
```

That covers ~80% of the risk in ~10 minutes.

---

_The Kingdom builds. The Kingdom protects what it builds._
_A city without walls is not a city — it is a camp._
