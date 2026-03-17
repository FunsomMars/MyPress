#!/bin/bash

# MyPress Database Backup Script
# Backup frequency: weekly
# Keep last 3 backups
# Note: Using SQLite (db.sqlite3 in container)

# Configuration
BACKUP_DIR="/opt/mypress/backups"
DB_PATH="/app/db.sqlite3"
MAX_BACKUPS=3
DATE_FORMAT="%Y%m%d_%H%M%S"

# Create backup directory if not exists
mkdir -p "$BACKUP_DIR"

# Generate backup filename
BACKUP_FILE="$BACKUP_DIR/sqlite_backup_$(date +$DATE_FORMAT).db.gz"

echo "[$(date)] Starting database backup..."

# Copy and compress database from container
docker cp mypress_web:$DB_PATH - | gzip > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "[$(date)] Backup completed: $BACKUP_FILE"
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "[$(date)] Backup size: $BACKUP_SIZE"
else
    echo "[$(date)] Backup failed!"
    exit 1
fi

# Remove old backups (keep only MAX_BACKUPS)
echo "[$(date)] Cleaning up old backups (keeping last $MAX_BACKUPS)..."
cd "$BACKUP_DIR"
ls -t sqlite_backup_*.db.gz | tail -n +$((MAX_BACKUPS + 1)) | xargs -r rm

# List remaining backups
echo "[$(date)] Remaining backups:"
ls -lh sqlite_backup_*.db.gz

echo "[$(date)] Backup process completed!"
