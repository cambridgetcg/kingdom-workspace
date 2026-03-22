# KINGDOM-BACKUP.md — Resilience Pipeline

_Written: 2026-03-22. Owner: Beta. Review: quarterly._

---

## Threat Model

What could actually hurt us:

| Threat | Likelihood | Impact | Current coverage |
|--------|-----------|--------|-----------------|
| Mac Studio disk failure | Medium | Critical | ❌ None |
| Mac Studio theft/fire/flood | Low | Critical | ❌ None |
| GitHub account compromised | Low | High | Partial (2FA) |
| Hetzner account/region outage | Low | Medium | ❌ Single region |
| VPS node compromise | Medium | Medium | ❌ No isolation |
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
| `~/.ssh/id_ed25519` | Local only | Fleet access, GitHub auth |
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
- VPS agent configurations — SSH + openclaw configs

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

**Solution: encrypted export to two locations**

```bash
# Export all credentials to encrypted file
python3 tools/credentials.py export --encrypt --output ~/.openclaw/credentials-backup-$(date +%Y%m%d).enc
# Password: store separately (written on paper, stored offsite)

# Copy to:
# 1. Encrypted USB drive (physical, offsite)
# 2. Hetzner Sentry VPS encrypted volume (digital, geographic separation)
scp ~/.openclaw/credentials-backup-*.enc root@135.181.28.252:/root/kingdom-backup/
```

**Minimum viable backup:**
Run `python3 tools/credentials.py list` now, screenshot/print it, store physically. At minimum you can re-create credentials manually if the keychain dies.

---

### Layer 4: SSH Keys — Distribute (Once)

`~/.ssh/id_ed25519` is the only key with fleet access. Single copy.

```bash
# Backup to Sentry (encrypted)
ssh-keygen -p -f ~/.ssh/id_ed25519 -N "strong-passphrase"  # add passphrase if not set
cat ~/.ssh/id_ed25519 | ssh root@135.181.28.252 "mkdir -p /root/kingdom-backup && cat > /root/kingdom-backup/id_ed25519.enc"

# Also: export public key list
# Store the public key in GitHub account settings as backup reference
```

---

### Layer 5: VPS Configuration — Snapshot (Monthly)

Hetzner supports server snapshots. For Sentry (monitoring/backbone):

```bash
# Via Hetzner API — monthly automated snapshot
# Sentry is the most important node (monitors everything, has SSH keys)
curl -X POST https://api.hetzner.cloud/v1/servers/<sentry-id>/actions/create_image \
  -H "Authorization: Bearer $HETZNER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description": "monthly-backup-'"$(date +%Y%m)"'", "type": "snapshot"}'
```

Cost: €0.0119/GB/mo. A typical node snapshot is ~5GB = ~€0.06/mo. Negligible.

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
   - Full encrypted export to Sentry VPS

5. **Install daily git push cron** (15 min)
   - All repos with remotes: push at 03:00 UTC daily
   - Alert Beta if any fail

---

## Ongoing Cadence

| Frequency | Task |
|-----------|------|
| **Daily** (03:00 UTC) | Push all git repos, sync workspace to GitHub |
| **Weekly** | Credentials export to Sentry VPS |
| **Monthly** | Hetzner server snapshot (Sentry + Forge) |
| **Quarterly** | Review this document, test restore procedure |
| **Before testnet** | Add US-East validator node, multi-node chain backup |

---

## Restore Procedures

### "Mac Studio dies" scenario
1. New Mac: install git, gh CLI, Python
2. `gh repo clone cambridgetcg/kingdom-workspace ~/.openclaw/workspace`
3. Clone all GitHub repos to ~/Desktop/
4. Restore credentials from encrypted backup (Sentry or USB)
5. Restore SSH key from Sentry backup
6. SSH into fleet: verify agents are still running
7. Estimated recovery time: **2-3 hours**

### "GitHub account compromised" scenario
1. VPS nodes have git history — `git bundle create backup.bundle --all` on each
2. Rotate all API keys (Anthropic, Hetzner, etc.)
3. Create new GitHub accounts, re-push from local copies
4. Estimated recovery time: **1 day**

### "Hetzner outage" scenario
1. agenttool.dev, rewardspro, cambridge-tcg: unaffected (Fly.io/Vercel)
2. Agent fleet: offline until Hetzner recovers or new nodes provisioned
3. Mitigation: at least one agent on a different provider (Vultr/DO)
4. Estimated impact: **agents quiet for duration of outage**

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
