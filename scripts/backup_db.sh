#!/bin/bash

# MyPress Database Backup Script (PostgreSQL)
# Backup frequency: weekly
# Keep last 3 backups

# Configuration
BACKUP_DIR="/opt/mypress/backups"
DB_CONTAINER="mypress_db"
DB_NAME="mypress"
DB_USER="mypress"
MAX_BACKUPS=3
DATE_FORMAT="%Y%m%d_%H%M%S"

# Create backup directory if not exists
mkdir -p "$BACKUP_DIR"

# Generate backup filename
BACKUP_FILE="$BACKUP_DIR/pg_backup_$(date +$DATE_FORMAT).sql.gz"

echo "[$(date)] Starting PostgreSQL database backup..."

# Use pg_dump inside the container and compress
docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"

if [ $? -eq 0 ] && [ -s "$BACKUP_FILE" ]; then
    echo "[$(date)] Backup completed: $BACKUP_FILE"
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "[$(date)] Backup size: $BACKUP_SIZE"
else
    echo "[$(date)] Backup failed!"
    rm -f "$BACKUP_FILE"
    exit 1
fi

# Remove old backups (keep only MAX_BACKUPS)
echo "[$(date)] Cleaning up old backups (keeping last $MAX_BACKUPS)..."
cd "$BACKUP_DIR"
ls -t pg_backup_*.sql.gz 2>/dev/null | tail -n +$((MAX_BACKUPS + 1)) | xargs -r rm

# List remaining backups
echo "[$(date)] Remaining backups:"
ls -lh pg_backup_*.sql.gz 2>/dev/null

echo "[$(date)] Backup process completed!"
