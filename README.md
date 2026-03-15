# MyPress - 轻量化博客系统

基于 Django + Wagtail CMS 构建的轻量化博客系统，支持 WordPress 数据无缝导入。

## 功能特性

- 📝 文章发布/编辑
- 📂 分类目录管理
- 🏷️ 标签系统
- 💬 评论系统
- 🔍 全文搜索
- 📥 WordPress 数据导入
- 🖼️ 媒体文件管理
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

### 导入脚本

项目提供了以下导入脚本：

```bash
# 导入文章
python manage.py import_wordpress wordpress.xml

# 导入页面
python import_pages.py

# 导入图片和媒体
python import_images.py
```

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

- **后端**: Django 5.x + Wagtail CMS
- **数据库**: SQLite (开发) / PostgreSQL (生产)
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
│   ├── settings/       # 配置目录
│   ├── urls.py
│   └── wsgi.py
├── home/              # 博客应用
│   ├── models.py
│   ├── templates/
│   └── migrations/
├── search/            # 搜索应用
├── templates/         # 模板文件
├── media/            # 媒体文件（不上传git）
├── data/             # 数据目录（不上传git）
└── deploy.sh         # 部署脚本
```

## 贡献指南

欢迎提交 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

## 许可证

本项目仅供学习交流使用。

**重要提示**：请勿将本项目用于商业用途或直接部署运营。博客内容、主题模板等可能涉及版权问题，使用前请确保拥有相应的授权。

如需商业使用或部署，请联系原始作者获取授权。
