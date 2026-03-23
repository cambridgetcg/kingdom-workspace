#!/bin/bash
# Kingdom daily backup push
cd /tmp  # ensure consistent starting directory — runs at 03:00 UTC
# Pushes all repos with remotes, syncs workspace memory

LOG="$HOME/.openclaw/workspace/memory/backup-log.txt"
echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) — backup-push starting" >> "$LOG"

REPOS=(
  "$HOME/Desktop/legible_money"
  "$HOME/Desktop/rewardspro"
  "$HOME/Desktop/cambridge-tcg"
  "$HOME/Desktop/prediction-markets"
  "$HOME/Desktop/agenttool-sdk-py"
  # "$HOME/Desktop/agenttool-sdk-ts" — handled separately (clean-main branch) # note: uses clean-main branch
  "$HOME/Desktop/agent-bootstrap"
  "$HOME/Desktop/agent-pulse"
  "$HOME/Desktop/agent-vault"
  "$HOME/Desktop/agenttool-dashboard"
  "$HOME/Desktop/agenttool-docs"
  "$HOME/Desktop/agenttool-landing"
  "$HOME/Desktop/agenttool-infra"
  "$HOME/Desktop/whitehack"
)

FAILED=0
for dir in "${REPOS[@]}"; do
  name=$(basename "$dir")
  if [ -d "$dir/.git" ]; then
    cd "$dir"
    # Use current branch if not on main
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)
    push_cmd="git push origin ${branch}:main"
    result=$($push_cmd 2>&1)
    if echo "$result" | grep -q "error\|fatal"; then
      echo "  FAIL: $name — $result" >> "$LOG"
      FAILED=$((FAILED+1))
    else
      echo "  OK: $name" >> "$LOG"
    fi
  fi
done

# Workspace memory sync
cd "$HOME/.openclaw/workspace"
git add -A
git commit -m "workspace sync $(date -u +%Y-%m-%d)" --allow-empty -q
git push origin main >> "$LOG" 2>&1

echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) — backup-push done (failures: $FAILED)" >> "$LOG"
