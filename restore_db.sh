#!/bin/bash

# MyPress Database Restore Script (for SQLite)
# Usage: ./restore_db.sh [backup_file]
# If no backup file specified, list available backups

BACKUP_DIR="/opt/mypress/backups"
DB_PATH="/app/db.sqlite3"

if [ $# -eq 0 ]; then
    echo "Available backups:"
    ls -lh "$BACKUP_DIR"/sqlite_backup_*.db.gz
    echo ""
    echo "Usage: $0 <backup_file>"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "Warning: This will overwrite the current database!"
echo "Backup file: $BACKUP_FILE"
echo ""
read -p "Are you sure you want to restore? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled."
    exit 0
fi

echo "Stopping web service..."
docker stop mypress_web 2>/dev/null

echo "Restoring database..."
gunzip -c "$BACKUP_FILE" | docker cp - mypress_web:$DB_PATH

if [ $? -eq 0 ]; then
    echo "Restore completed successfully!"
else
    echo "Restore failed!"
fi

echo "Starting web service..."
docker start mypress_web
