# MyPress - 轻量化博客系统

基于 Django + Wagtail CMS 构建的轻量化博客系统，支持 WordPress 数据无缝导入。

## 功能特性

- 📝 文章发布/编辑（支持 WordPress 短代码）
- 🎵 音频/视频播放支持
- 💬 评论系统（支持审核）
- 👥 用户组权限系统（编辑/版主/管理员）
- 📂 自定义页面管理
- 🔍 全文搜索
- 🖼️ 媒体文件管理
- 🐳 Docker 一键部署
- 📦 PostgreSQL 数据库（支持高并发）

## 快速开始

### 1. 使用 Docker 一键部署（推荐）

```bash
# 克隆项目
git clone https://github.com/FunsomMars/MyPress.git
cd MyPress

# 复制环境配置
cp .env.example .env

# 编辑 .env 文件
vim .env

# 一键部署
chmod +x deploy.sh
./deploy.sh
```

### 2. 本地开发

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 复制环境配置
cp .env.example .env

# 运行迁移
python manage.py migrate

# 启动开发服务器
python manage.py runserver
```

访问地址：
- 前台: `http://localhost:8000`
- 管理后台: `http://localhost:8000/admin/`

## 用户权限系统

| 用户组 | 权限 |
|--------|------|
| 普通用户 | 浏览、评论 |
| 编辑 | 创建/编辑文章 |
| 版主 | 评论管理 |
| 管理员 | 页面管理、用户审批 |
| 超级管理员 | 全部权限 |

### 权限申请
用户可在个人中心申请加入用户组，需管理员审批后生效。

## WordPress 数据导入

### 导入文章和页面

```bash
# 导入文章
python manage.py import_wordpress wordpress.xml

# 导入自定义页面
python import_pages_json.py
```

### 支持的短代码

- `[audio mp3="..."]` - 音频播放器
- `[video...]` - 视频播放器

## 配置说明

### 环境变量 (.env)

```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,www.mspace.top

# PostgreSQL
DB_NAME=mypress
DB_USER=mypress
DB_PASSWORD=your-password
DB_HOST=db
DB_PORT=5432

# 邮件（可选）
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
```

### 备份（生产环境）

```bash
# 手动备份
/opt/mypress/backup_db.sh

# 自动备份（每周日凌晨3点）
# 备份保留4周
```

## 常用命令

```bash
# 进入容器
docker exec -it mypress_web bash

# 查看日志
docker logs -f mypress_web

# 重启服务
docker restart mypress_web

# 重建容器
docker-compose up -d --build
```

## 技术栈

- **后端**: Django 5.x + Wagtail CMS 6.x
- **数据库**: PostgreSQL 15
- **缓存**: Redis 7
- **前端**: Bootstrap 5 + 自定义 CSS
- **部署**: Docker + Docker Compose + Nginx

## 目录结构

```
MyPress/
├── docker-compose.yml    # Docker编排
├── Dockerfile           # Docker镜像
├── requirements.txt     # Python依赖
├── manage.py           # Django管理脚本
├── deploy.sh          # 部署脚本
├── my_press/          # Django项目配置
│   ├── settings/      # 配置目录
│   ├── urls.py
│   └── wsgi.py
├── home/              # 博客应用
│   ├── models.py      # 数据模型
│   ├── views.py       # 视图
│   ├── templates/     # 模板
│   └── templatetags/  # 模板标签
├── search/            # 搜索应用
├── data/              # 导入数据（JSON）
└── media/            # 媒体文件
```

## 许可证

MIT License - 仅供学习交流使用。
