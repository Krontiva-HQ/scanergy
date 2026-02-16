#!/usr/bin/env bash
# ============================================
# Scarnergy Backup
# ============================================
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_USER="${DB_USER:-postgres}"
DB_NAME="${DB_NAME:-scarnergy}"

mkdir -p "$BACKUP_DIR"

echo "Scarnergy Backup — $TIMESTAMP"

# PostgreSQL dump
echo "  Backing up PostgreSQL..."
docker exec scarnergy-db pg_dump -U "$DB_USER" -d "$DB_NAME" --format=custom \
  > "$BACKUP_DIR/scarnergy_db_${TIMESTAMP}.dump"
echo "  → $BACKUP_DIR/scarnergy_db_${TIMESTAMP}.dump"

# Storage volumes
echo "  Backing up storage..."
docker run --rm -v scarnergy-v2_storage_data:/data -v "$(pwd)/$BACKUP_DIR":/backup \
  alpine tar czf "/backup/storage_${TIMESTAMP}.tar.gz" -C /data .
echo "  → $BACKUP_DIR/storage_${TIMESTAMP}.tar.gz"

# MQTT data
echo "  Backing up MQTT..."
docker run --rm -v scarnergy-v2_mqtt_data:/data -v "$(pwd)/$BACKUP_DIR":/backup \
  alpine tar czf "/backup/mqtt_${TIMESTAMP}.tar.gz" -C /data .
echo "  → $BACKUP_DIR/mqtt_${TIMESTAMP}.tar.gz"

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.dump" -mtime +30 -delete 2>/dev/null || true
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete 2>/dev/null || true

echo "Backup complete."
