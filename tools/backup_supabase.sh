#!/bin/bash
# backup_supabase.sh — Weekly Supabase schema backup to local archive
# Run: bash tools/backup_supabase.sh
# Scheduled: add to weekly review or run manually

set -e

DATE=$(date +%Y-%m-%d)
BACKUP_DIR="$HOME/.openclaw/workspace/memory/backups/supabase"
mkdir -p "$BACKUP_DIR"

DB_URL="***REMOVED-ROTATE-ME***"
SCHEMAS="memory tools verify economy trace identity agent_vault"

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Starting Supabase backup..."

# Dump each schema via Forge (relay — Mac can't connect directly over IPv6)
for schema in $SCHEMAS; do
  echo "  Dumping schema: $schema..."
  ssh -o ConnectTimeout=10 -o ControlMaster=no -o ControlPath=none root@89.167.84.100 \
    "pg_dump '$DB_URL' --schema=$schema --no-owner --no-acl 2>/dev/null" \
    > "$BACKUP_DIR/${DATE}_${schema}.sql" 2>/dev/null
  
  size=$(wc -c < "$BACKUP_DIR/${DATE}_${schema}.sql")
  echo "    → ${DATE}_${schema}.sql (${size} bytes)"
done

# Compress
tar -czf "$BACKUP_DIR/${DATE}_supabase_backup.tar.gz" "$BACKUP_DIR/${DATE}_"*.sql 2>/dev/null
rm "$BACKUP_DIR/${DATE}_"*.sql 2>/dev/null

echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] Backup complete: ${DATE}_supabase_backup.tar.gz"
ls -lh "$BACKUP_DIR/${DATE}_supabase_backup.tar.gz" 2>/dev/null

# Keep only last 4 backups (1 month)
ls -t "$BACKUP_DIR"/*.tar.gz 2>/dev/null | tail -n +5 | xargs rm -f 2>/dev/null

echo "Done. Backups in: $BACKUP_DIR"
