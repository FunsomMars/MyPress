# MyPress - 轻量化博客系统技术规格文档

## 1. 项目概述

**项目名称**: MyPress  
**项目类型**: 基于Django的轻量化博客系统  
**核心功能**: WordPress数据无缝导入、博客文章管理、用户评论、注册用户系统  
**目标用户**: 从WordPress迁移到自托管博客的开发者/博主

## 2. 技术栈

- **后端框架**: Django 4.2 + Mezzanine CMS
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **前端框架**: Bootstrap 5 + 自定义主题
- **部署环境**: Docker + Docker Compose (x86_64)
- **Python版本**: 3.9+

## 3. 功能规格

### 3.1 核心博客功能
- [x] 文章发布/编辑/删除
- [x] 分类目录管理
- [x] 标签系统
- [x] 文章搜索
- [x] 文章归档（按月份/分类）
- [x] Markdown/Rich Text编辑器

### 3.2 用户系统
- [x] 用户注册/登录
- [x] 用户权限管理
- [x] 用户个人资料页面
- [x] 密码重置功能

### 3.3 评论系统
- [x] 文章评论
- [x] 评论审核机制
- [x] 评论回复
- [x] 评论邮件通知（可选）

### 3.4 WordPress导入
- [x] WXR (WordPress eXtended RSS) 格式导入
- [x] 文章导入
- [x] 分类/标签导入
- [x] 评论导入
- [x] 媒体文件URL保留

### 3.5 部署功能
- [x] Docker一键部署
- [x] docker-compose编排
- [x] 环境变量配置
- [x] 数据持久化

## 4. UI/UX 设计方向

### 视觉风格
- 简洁现代的博客风格
- 响应式设计（移动端友好）
- 注重阅读体验

### 配色方案
- 主色调: #2c3e50 (深蓝灰)
- 强调色: #3498db (明亮蓝)
- 背景色: #ffffff / #f8f9fa
- 文字色: #333333

### 布局
- 经典博客布局：侧边栏 + 主内容区
- 顶部导航
- 页脚信息

## 5. 文件结构

```
my_press/
├── docker-compose.yml      # Docker编排配置
├── Dockerfile              # Docker镜像配置
├── requirements.txt        # Python依赖
├── my_press/               # Django项目目录
│   ├── settings.py         # Django设置
│   ├── urls.py             # URL路由
│   └── wsgi.py             # WSGI配置
├── blog/                   # 博客应用
│   ├── models.py           # 数据模型
│   ├── views.py            # 视图函数
│   ├── admin.py            # 管理后台
│   └── management/         # 管理命令
├── templates/              # 模板文件
├── static/                # 静态文件
├── .env.example           # 环境变量示例
├── deploy.sh              # 一键部署脚本
└── SPEC.md                # 本规格文档
```

## 6. 验收标准

1. ✅ 能够通过docker-compose一键启动服务
2. ✅ 能够成功导入WordPress WXR文件
3. ✅ 前端页面美观、响应式
4. ✅ 用户可以注册、登录、发表评论
5. ✅ 文章、分类、标签功能完整
6. ✅ 生产环境可用（PostgreSQL配置）
