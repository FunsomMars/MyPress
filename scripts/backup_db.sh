#!/bin/bash

# MyPress 数据库备份脚本
# 用法: ./scripts/backup_db.sh
# 建议通过 crontab 定时执行:
#   0 3 * * * /opt/mypress/scripts/backup_db.sh >> /var/log/mypress_backup.log 2>&1

set -e

# 配置
BACKUP_DIR="${BACKUP_DIR:-/opt/mypress/backups}"
DB_CONTAINER="${DB_CONTAINER:-mypress_db}"
DB_NAME="${DB_NAME:-mypress}"
DB_USER="${DB_USER:-mypress}"
MAX_BACKUPS=${MAX_BACKUPS:-7}

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 生成备份文件名
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/pg_backup_${TIMESTAMP}.sql.gz"

echo "[$(date)] 开始备份 PostgreSQL 数据库..."

# 检查容器是否运行
if ! docker ps --format '{{.Names}}' | grep -q "^${DB_CONTAINER}$"; then
    echo "[$(date)] 错误: 数据库容器 ${DB_CONTAINER} 未运行"
    exit 1
fi

# 执行备份
docker exec "$DB_CONTAINER" pg_dump -U "$DB_USER" "$DB_NAME" | gzip > "$BACKUP_FILE"

if [ $? -eq 0 ] && [ -s "$BACKUP_FILE" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "[$(date)] 备份成功: $BACKUP_FILE ($BACKUP_SIZE)"
else
    echo "[$(date)] 备份失败!"
    rm -f "$BACKUP_FILE"
    exit 1
fi

# 清理旧备份
echo "[$(date)] 清理旧备份（保留最近 $MAX_BACKUPS 份）..."
cd "$BACKUP_DIR"
REMOVED=$(ls -t pg_backup_*.sql.gz 2>/dev/null | tail -n +$((MAX_BACKUPS + 1)))
if [ -n "$REMOVED" ]; then
    echo "$REMOVED" | xargs rm -f
    echo "[$(date)] 已删除: $(echo "$REMOVED" | wc -l) 份旧备份"
fi

# 列出当前备份
echo "[$(date)] 当前备份列表:"
ls -lh pg_backup_*.sql.gz 2>/dev/null

echo "[$(date)] 备份完成!"
