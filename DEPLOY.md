# MyPress 部署指南

## 快速部署

### 1. 克隆代码
```bash
git clone https://github.com/FunsomMars/MyPress.git
cd MyPress
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 设置域名和数据库密码
```

### 3. 启动Docker容器
```bash
docker compose up -d
```

### 4. 导入数据库 (从WordPress迁移)
```bash
# 从旧服务器复制数据库备份和媒体文件
scp user@old-server:/path/to/backup.sql.gz ./
scp -r user@old-server:/var/www/html/wp-content/uploads ./media/

# 导入数据库
zcat backup.sql.gz | docker exec -i mypress_db psql -U mypress -d mypress

# 修复Site配置
docker exec mypress_web python manage.py shell -c "
from wagtail.models import Site, Page
site = Site.objects.first()
site.hostname = 'your-domain.com'
site.save()
"
```

### 5. 配置Nginx
```bash
cp nginx.conf.example /etc/nginx/sites-available/mypress
# 修改域名
sed -i 's/YOUR_DOMAIN/your-domain.com/g' /etc/nginx/sites-available/mypress
ln -s /etc/nginx/sites-available/mypress /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

## 从WordPress导入数据

### 媒体文件
WordPress的媒体文件位于 `wp-content/uploads/`，需要复制到 `/var/www/media/uploads/`

### 数据库
Wagtail数据库通常比WordPress小，可以使用pg_dump/pg_restore迁移。

## 环境要求
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+
- Nginx (可选，使用Docker亦可)
