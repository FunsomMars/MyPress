# MyPress 部署指南

## 一、快速部署（推荐）

### 1. 准备服务器

- 操作系统：Debian/Ubuntu 或 CentOS
- 最低配置：1核 CPU / 1GB 内存 / 20GB 磁盘
- 安装 Docker 和 Docker Compose

```bash
# Debian/Ubuntu 安装 Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker && systemctl start docker
```

### 2. 克隆代码

```bash
cd /opt
git clone https://github.com/FunsomMars/MyPress.git mypress
cd mypress
```

### 3. 一键部署

```bash
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

脚本会自动完成：
- 生成 `.env` 配置文件（含随机 SECRET_KEY 和数据库密码）
- 创建数据目录和静态文件目录
- 构建 Docker 镜像
- 启动 Web、PostgreSQL、Redis 三个容器
- 等待健康检查通过
- 提示创建超级管理员

### 4. 创建超级管理员

```bash
docker exec -it mypress_web python manage.py createsuperuser
```

### 5. 配置 Nginx（生产环境必需）

```bash
# 复制配置模板
cp nginx.conf.example /etc/nginx/sites-available/mypress

# 替换域名
sed -i 's/YOUR_DOMAIN/your-domain.com/g' /etc/nginx/sites-available/mypress
sed -i 's/YOUR_WWW_DOMAIN/www.your-domain.com/g' /etc/nginx/sites-available/mypress

# 启用站点
ln -s /etc/nginx/sites-available/mypress /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

#### 配置 SSL（推荐 Let's Encrypt）

```bash
apt install certbot python3-certbot-nginx
certbot --nginx -d your-domain.com -d www.your-domain.com
```

### 6. 验证部署

```bash
curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/
# 应返回 200
```

---

## 二、WordPress 数据迁移

### 1. 迁移媒体文件

```bash
# 从旧 WordPress 服务器复制 uploads 目录
scp -r user@old-server:/var/www/html/wp-content/uploads/* /var/www/media/uploads/

# 确保目录权限正确
chown -R www-data:www-data /var/www/media/
```

### 2. 准备文章数据

将 WordPress 文章导出为 JSON，放入 `data/posts.json`：

```json
[
  {
    "title": "文章标题",
    "slug": "unique-slug",
    "content": "<p>HTML 格式正文</p>",
    "date": "2024-01-15"
  }
]
```

### 3. 准备页面数据

将自定义页面数据放入 `data/pages.json`，格式同上。

### 4. 执行导入

```bash
# 重启服务自动导入（init_pages 命令在启动时运行）
docker compose restart web

# 或手动执行
docker exec mypress_web python manage.py init_pages
```

### 5. 验证导入

```bash
# 检查文章数量
docker exec mypress_web python manage.py shell -c "
from home.models import BlogPage
print(f'文章总数: {BlogPage.objects.count()}')
"
```

---

## 三、环境变量说明

配置文件：`.env`（从 `.env.example` 复制）

| 变量 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `SECRET_KEY` | 是 | - | Django 密钥，部署脚本自动生成 |
| `ALLOWED_HOSTS` | 是 | localhost | 允许的域名，逗号分隔 |
| `DB_NAME` | 是 | mypress | PostgreSQL 数据库名 |
| `DB_USER` | 是 | mypress | 数据库用户名 |
| `DB_PASSWORD` | 是 | - | 数据库密码，部署脚本自动生成 |
| `DEBUG` | 否 | False | 调试模式，生产环境必须为 False |
| `MYPRESS_PORT` | 否 | 8000 | Web 服务端口 |
| `REDIS_URL` | 否 | redis://redis:6379/0 | Redis 连接地址 |
| `TIME_ZONE` | 否 | Asia/Shanghai | 时区 |

---

## 四、日常运维

### 更新代码

```bash
cd /opt/mypress
git pull origin master
docker compose restart web
```

如果修改了 `Dockerfile` 或 `requirements.txt`：

```bash
docker compose up -d --build web
```

### 数据库备份

```bash
# 手动备份
./scripts/backup_db.sh

# 设置每天凌晨 3 点自动备份
crontab -e
0 3 * * * /opt/mypress/scripts/backup_db.sh >> /var/log/mypress_backup.log 2>&1
```

备份保存在 `/opt/mypress/backups/`，自动保留最近 7 份。

### 数据库恢复

```bash
zcat /opt/mypress/backups/pg_backup_YYYYMMDD_HHMMSS.sql.gz | \
  docker exec -i mypress_db psql -U mypress -d mypress
```

### 查看日志

```bash
# 实时日志
docker compose logs -f web

# 最近 100 行
docker compose logs --tail 100 web
```

### 磁盘清理

```bash
# 清理未使用的 Docker 镜像
docker image prune -f

# 清理未使用的 Docker 卷
docker volume prune -f

# 清理 apt 缓存
apt-get clean

# 清理旧日志
journalctl --vacuum-time=7d
```

---

## 五、架构说明

```
            ┌──────────┐
            │  Nginx   │  :80/:443
            │(宿主机)   │  SSL + 静态文件 + 媒体文件
            └────┬─────┘
                 │ proxy_pass :8000
            ┌────┴─────┐
            │   Web    │  Django + Wagtail
            │(容器)     │  runserver :8000
            └──┬───┬───┘
               │   │
     ┌─────────┘   └─────────┐
     │                       │
┌────┴─────┐           ┌────┴─────┐
│ PostgreSQL│           │  Redis   │
│  (容器)   │           │  (容器)   │
│  :5432    │           │  :6379   │
└──────────┘           └──────────┘
```

### 数据卷

| 宿主机路径 | 容器路径 | 用途 |
|-----------|---------|------|
| `/opt/mypress/data` | `/app/data` | 导入数据（JSON） |
| `/var/www/static` | `/app/static` | 静态文件（CSS/JS/图片） |
| `/var/www/media/uploads` | `/app/media` | 媒体文件（上传+WordPress） |
| `/opt/mypress/home` | `/app/home` | 应用代码（热更新） |
| `/opt/mypress/my_press` | `/app/my_press` | 项目配置（热更新） |
| `/opt/mypress/templates` | `/app/templates` | 模板文件（热更新） |
| `db_data`（Docker卷） | PostgreSQL 数据 | 数据库持久化 |

---

## 六、故障排查

### 502 Bad Gateway

容器可能还在启动，等待 5-10 秒后重试。查看日志：

```bash
docker compose logs --tail 50 web
```

### 500 Internal Server Error

```bash
# 查看详细错误
docker compose logs --tail 100 web 2>&1 | grep -i error

# 常见原因：
# 1. SECRET_KEY 未设置 → 检查 .env 和 production.py
# 2. 静态文件缺失 → docker exec mypress_web python manage.py collectstatic --noinput
# 3. 数据库迁移未执行 → docker exec mypress_web python manage.py migrate
```

### 模板标签报错

```
TemplateSyntaxError: 'xxx' is not a registered tag library
```

确保模板标签文件在 `home/templatetags/` 目录下（不是项目根目录），且 `home` 在 `INSTALLED_APPS` 中。

### 静态文件 404

```bash
# 重新收集静态文件
docker exec mypress_web python manage.py collectstatic --clear --noinput
```

### 连接数据库失败

```bash
# 检查数据库容器状态
docker compose ps db
docker compose logs db

# 验证连接
docker exec mypress_db pg_isready -U mypress
```
