# MyPress - 轻量化博客系统

[English](./README.md) | 简体中文

基于 Django 6 + Wagtail CMS 构建的轻量化博客系统，支持 WordPress 数据无缝导入，Docker 一键部署。

## 功能特性

**内容管理**
- 文章发布/编辑（富文本编辑器，TinyMCE 语言自动跟随浏览器）
- 自定义页面管理（随笔、视频、音乐等栏目）
- WordPress 短代码支持（`[audio]`、`[video]`）
- 全文搜索
- 媒体文件管理

**用户系统**
- 邮箱注册验证（24小时有效）
- 登录会话控制（"记住我"14天 / 默认8小时）
- 五级权限体系：游客 → 普通用户 → 编辑 → 版主 → 管理员 → 超级管理员
- 用户组申请与审批流程

**评论系统**
- 支持登录用户和游客评论
- 评论审核机制（可配置）
- 评论管理后台

**部署运维**
- Docker Compose 一键部署
- PostgreSQL 15 + Redis 7
- Nginx 反向代理 + SSL
- 自动数据库备份
- WordPress 数据一键导入
- 响应式布局，适配手机/平板/桌面

## 快速开始

### 环境要求

- Docker 20+ 和 Docker Compose
- 1 核 CPU / 1GB 内存以上
- 域名（可选，用于 SSL）

### 一键部署

```bash
git clone https://github.com/FunsomMars/MyPress.git
cd MyPress

# 编辑配置（站点名称、管理员账号等）
cp .env.example .env
vim .env

# 一键部署
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

部署前建议修改 `.env` 中的关键配置：

```env
# 站点自定义
SITE_NAME=我的博客
HERO_TITLE=欢迎来到我的博客
HERO_SUBTITLE=分享技术、生活与创意

# 超级管理员（首次启动自动创建）
SUPERUSER_USERNAME=admin
SUPERUSER_PASSWORD=your-secure-password
SUPERUSER_EMAIL=admin@example.com
```

部署脚本会自动：
1. 检查 Docker 环境
2. 生成 SECRET_KEY 和数据库密码（如 `.env` 不存在）
3. 创建必要目录
4. 构建镜像并启动服务
5. 等待健康检查通过
6. 自动创建超级管理员（从 `.env` 读取）

部署完成后访问：
- 前台：`http://your-server:8000`
- Wagtail 后台：`http://your-server:8000/admin/`

### 本地开发

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

python manage.py migrate
python manage.py init_pages          # 初始化页面结构
python manage.py createsuperuser     # 创建管理员
python manage.py runserver
```

本地默认使用 SQLite，无需 PostgreSQL。

## WordPress 数据导入

MyPress 支持从 WordPress 导入文章和媒体文件。

### 1. 导出 WordPress 数据

从旧 WordPress 服务器复制媒体文件：

```bash
# 复制媒体文件到 MyPress 的媒体目录
scp -r user@wordpress-server:/var/www/html/wp-content/uploads/* /var/www/media/uploads/
```

### 2. 导入文章

将文章数据转为 JSON 格式，放入 `data/posts.json`：

```json
[
  {
    "title": "文章标题",
    "slug": "article-slug",
    "content": "<p>HTML内容</p>",
    "date": "2024-01-15"
  }
]
```

重启服务后 `init_pages` 命令会自动导入：

```bash
docker compose restart web
```

或手动导入：

```bash
docker exec mypress_web python manage.py init_pages
```

### 3. 自定义页面

将页面数据放入 `data/pages.json`，格式同上。`init_pages` 命令会自动创建以下页面：

| Slug | 页面名称 |
|------|---------|
| essay | 日常随笔 |
| about | 关于 |
| video | 视频剪辑 |
| music | 云音乐歌单 |
| linux | 学点Linux |
| jokes | 段子手段子 |
| files | 文件管理 |
| concept | 学点概念 |
| privacy | 隐私政策 |

### 支持的 WordPress 短代码

- `[audio mp3="url"]` → HTML5 音频播放器
- `[video src="url"]` → HTML5 视频播放器

## 用户权限体系

| 角色 | 权限 |
|------|------|
| 游客 | 浏览文章、查看页面 |
| 普通用户 | + 发表评论、申请用户组 |
| 编辑 | + 创建/编辑自己的文章 |
| 版主 | + 删除任意文章、管理评论 |
| 管理员 | + 编辑自定义页面、权限审批 |
| 超级管理员 | 全部权限 + 用户管理、系统管理 |

用户注册后为普通用户，可在个人中心申请加入更高权限组，由超级管理员审批。

## 配置说明

### 环境变量 (.env)

```env
# 必需（部署脚本自动生成）
SECRET_KEY=your-secret-key
DB_PASSWORD=your-password
ALLOWED_HOSTS=localhost,example.com

# 站点自定义
SITE_NAME=MyPress                      # 导航栏标题 + 浏览器标签
HERO_TITLE=欢迎来到我的博客              # 首页大标题
HERO_SUBTITLE=分享技术、生活与创意        # 首页副标题
FOOTER_TEXT=                            # 页脚文字（留空则不显示）

# 超级管理员（首次启动自动创建，已存在则跳过）
SUPERUSER_USERNAME=admin
SUPERUSER_PASSWORD=change-this
SUPERUSER_EMAIL=admin@example.com
```

完整配置参见 [.env.example](.env.example)。

### Nginx 配置

生产环境推荐使用 Nginx 反向代理：

```bash
cp nginx.conf.example /etc/nginx/sites-available/mypress
# 修改 YOUR_DOMAIN 为实际域名
sed -i 's/YOUR_DOMAIN/example.com/g' /etc/nginx/sites-available/mypress
ln -s /etc/nginx/sites-available/mypress /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

Nginx 直接 serve 静态文件和媒体文件，性能更优：
- 静态文件：`/var/www/static/`
- 媒体文件：`/var/www/media/uploads/`

## 运维管理

### 数据库备份

```bash
# 手动备份
./scripts/backup_db.sh

# 设置定时备份（每天凌晨3点）
crontab -e
0 3 * * * /opt/mypress/scripts/backup_db.sh >> /var/log/mypress_backup.log 2>&1
```

备份文件保存在 `/opt/mypress/backups/`，自动保留最近7份。

### 常用命令

```bash
# 查看日志
docker compose logs -f web

# 重启服务
docker compose restart web

# 进入容器
docker exec -it mypress_web bash

# Django shell
docker exec -it mypress_web python manage.py shell

# 重建镜像（代码大改后）
docker compose up -d --build web

# 更新代码并重启（日常）
cd /opt/mypress && git pull origin master && docker compose restart web
```

### 数据库恢复

```bash
# 从备份恢复
zcat /opt/mypress/backups/pg_backup_YYYYMMDD_HHMMSS.sql.gz | \
  docker exec -i mypress_db psql -U mypress -d mypress
```

## 技术栈

| 组件 | 版本 |
|------|------|
| Python | 3.12 |
| Django | 6.x |
| Wagtail CMS | 7.3 |
| PostgreSQL | 15 |
| Redis | 7 |
| TinyMCE | 6.8 |
| Docker Compose | v2+ |

## 目录结构

```
MyPress/
├── docker-compose.yml         # Docker 服务编排
├── Dockerfile                 # 容器镜像定义
├── requirements.txt           # Python 依赖
├── .env.example               # 环境变量模板
├── nginx.conf.example         # Nginx 配置模板
├── scripts/
│   ├── deploy.sh              # 一键部署脚本
│   └── backup_db.sh           # 数据库备份脚本
├── my_press/                  # Django 项目配置
│   ├── settings/
│   │   ├── base.py            # 基础配置
│   │   ├── production.py      # 生产环境
│   │   └── dev.py             # 开发环境
│   ├── urls.py                # URL 路由
│   └── templates/base.html    # 基础模板（备用）
├── home/                      # 主应用
│   ├── models.py              # 数据模型
│   ├── views.py               # 视图逻辑
│   ├── templates/home/        # 页面模板
│   ├── templatetags/          # 自定义模板标签
│   ├── management/commands/   # 管理命令
│   └── static/                # 静态资源
├── templates/                 # 全局模板
│   └── base.html              # 基础模板
├── search/                    # 搜索功能
├── data/                      # 导入数据
│   ├── posts.json             # WordPress 文章
│   └── pages.json             # 自定义页面
└── media/                     # 媒体文件（运行时）
```

## 许可证

GNU General Public License v3.0
