#!/bin/bash
# backup_supabase.sh — Weekly Supabase schema backup to local archive
# Add to cron: 0 2 * * 0 bash ~/.openclaw/workspace/tools/backup_supabase.sh

set -e

BACKUP_DIR="$HOME/.openclaw/workspace/memory/backups/supabase"
DATE=$(date +%Y-%m-%d)
DB_URL="***REMOVED-ROTATE-ME***"

mkdir -p "$BACKUP_DIR"

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Starting Supabase backup..."

# Dump each Kingdom schema
for schema in memory tools verify economy trace identity agent_vault; do
  OUT="$BACKUP_DIR/${DATE}-${schema}.sql.gz"
  # Use Forge as relay (Mac can't reach Supabase IPv6 directly)
  ssh -o ConnectTimeout=10 -o ControlMaster=no -o ControlPath=none root@89.167.84.100 \
    "pg_dump '$DB_URL' --schema=$schema --no-owner --no-acl 2>/dev/null | gzip" \
    > "$OUT" 2>/dev/null && \
    echo "  ✅ $schema → $(du -sh $OUT | cut -f1)" || \
    echo "  ⚠️  $schema backup failed"
done

# Keep last 4 weeks only
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +28 -delete

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Backup complete."
