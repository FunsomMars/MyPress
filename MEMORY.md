# MEMORY.md - 长期记忆

## MyPress 项目规范

### 代码管理
- 本地开发完成后需及时 commit 上库
- OpenClaw 配置文件（.openclaw/、AGENTS.md、MEMORY.md 等）不需要上库

### 测试规范
- 每个功能点开发完成后需补充单元测试用例
- 功能开发完成后需本地跑全量基础功能用例，确保无回归
- 每次修改需同步到生产环境

### 生产环境
- 访问：ssh root@www.mspace.top
- 部署方式：Docker
- 备份路径：/opt/mypress/backups（每次修改前备份数据库）

### 旧数据迁移
- 旧 WordPress：ssh root@23.105.198.164
- 支持无缝导入迁移
