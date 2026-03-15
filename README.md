# MyPress - 轻量化博客系统

基于 Django + Mezzanine CMS 构建的轻量化博客系统，支持 WordPress 数据无缝导入。

## 功能特性

- 📝 文章发布/编辑/支持Markdown
- 📂 分类目录管理
- 🏷️ 标签系统
- 👥 用户注册/登录
- 💬 评论系统
- 🔍 全文搜索
- 📥 WordPress WXR 格式数据导入
- 🐳 Docker 一键部署

## 快速开始

### 1. 使用 Docker 一键部署（推荐）

```bash
# 克隆或下载项目
cd my_press

# 复制环境配置
cp .env.example .env

# 编辑 .env 文件，修改必要配置
vim .env

# 一键部署
chmod +x deploy.sh
./deploy.sh
```

### 2. 本地开发

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 复制环境配置
cp .env.example .env

# 编辑 .env 文件
vim .env

# 运行迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
```

### 3. Docker Compose 单独部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## WordPress 数据导入

### 方式一：管理命令导入

```bash
# 在容器内执行
docker-compose exec web python manage.py import_wordpress /path/to/wordpress.xml

# 或者本地
python manage.py import_wordpress wordpress.xml --author admin
```

### 方式二：Web界面上传导入

访问 `http://localhost:8000/import/` 上传 WXR 文件

### WordPress 导出步骤

1. 登录 WordPress 后台
2. 进入「工具」→「导出」
3. 选择「所有内容」
4. 点击「下载导出文件」
5. 将下载的 XML 文件导入到 MyPress

## 配置说明

### 环境变量 (.env)

```env
# Django 必需设置
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库
DB_NAME=mypress
DB_USER=mypress
DB_PASSWORD=your-password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# 邮件配置
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password

# 其他
TIME_ZONE=Asia/Shanghai
LANGUAGE_CODE=zh-hans
```

### Docker 部署

访问以下地址：

- 前台首页: `http://localhost:8000`
- 管理后台: `http://localhost:8000/admin/`
- 导入页面: `http://localhost:8000/import/`

## 常用命令

```bash
# 进入容器
docker-compose exec web bash

# 查看日志
docker-compose logs -f web

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 重新构建
docker-compose build --no-cache
```

## 技术栈

- **后端**: Django 4.2 + Mezzanine CMS
- **数据库**: PostgreSQL 15
- **缓存**: Redis 7
- **前端**: Bootstrap 5
- **部署**: Docker + Docker Compose

## 目录结构

```
my_press/
├── docker-compose.yml    # Docker编排
├── Dockerfile           # Docker镜像
├── requirements.txt     # Python依赖
├── manage.py           # Django管理脚本
├── my_press/          # Django项目配置
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── blog/              # 博客应用
│   ├── models.py
│   ├── admin.py
│   └── management/commands/
│       └── import_wordpress.py
├── templates/         # 模板文件
├── static/          # 静态文件
├── data/            # 数据目录
└── deploy.sh        # 部署脚本
```

## 许可证

MIT License
