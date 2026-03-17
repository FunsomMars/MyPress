# OpenClaw 技能库同步工具

一键同步 [awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills) 仓库中的技能到本地 OpenClaw。

## 功能特性

- 📦 从 GitHub 仓库自动同步 5409+ 个技能
- 🔍 按名称搜索和过滤技能
- ⚡ 批量安装技能
- 📝 列出已安装的技能
- 🧪 测试模式（不实际安装）

## 快速开始

### 方法 1: 使用快捷脚本（推荐）

```bash
# 查看帮助
~/workspace/scripts/skills-update.sh

# 同步前 10 个技能
~/workspace/scripts/skills-update.sh sync 10

# 搜索技能
~/workspace/scripts/skills-update.sh search weather

# 安装指定名称的技能
~/workspace/scripts/skills-update.sh install weather

# 列出已安装的技能
~/workspace/scripts/skills-update.sh list

# 测试模式（不实际安装）
~/workspace/scripts/skills-update.sh test
```

### 方法 2: 使用 Python 脚本

```bash
# 查看帮助
~/workspace/scripts/sync-skills.py --help

# 同步所有技能
~/workspace/scripts/sync-skills.py --sync

# 同步前 10 个技能
~/workspace/scripts/sync-skills.py --sync --limit 10

# 按名称过滤并同步
~/workspace/scripts/sync-skills.py --sync --filter "weather"

# 搜索可用技能
~/workspace/scripts/sync-skills.py --search "ai"

# 列出已安装的技能
~/workspace/scripts/sync-skills.py --list

# 测试模式（dry-run）
~/workspace/scripts/sync-skills.py --sync --limit 5 --dry-run
```

## 使用场景

### 场景 1: 安装天气相关技能

```bash
~/workspace/scripts/skills-update.sh install weather
```

### 场景 2: 探索 AI 相关技能

```bash
# 先搜索
~/workspace/scripts/skills-update.sh search ai

# 再选择安装
~/workspace/scripts/skills-update.sh install gpt
```

### 场景 3: 批量安装热门技能

```bash
# 安装前 50 个技能
~/workspace/scripts/skills-update.sh sync 50
```

### 场景 4: 查看已安装的技能

```bash
~/workspace/scripts/skills-update.sh list
```

## 技能安装位置

技能默认安装到 `~/.openclaw/skills/` 目录。

OpenClaw 会按以下优先级加载技能：
1. Workspace: `<workspace>/skills/`
2. Local: `~/.openclaw/skills/`
3. Bundled: OpenClaw 内置技能

## 常见问题

### Q: 如何一次性安装所有技能？
A: 可以运行 `~/workspace/scripts/skills-update.sh sync`，但这会安装所有 5409 个技能，需要很长时间。

### Q: 技能安装后如何使用？
A: 技能安装后会自动被 OpenClaw 识别，下次对话时可以直接使用。每个技能的具体用法请参考其 `SKILL.md` 文件。

### Q: 如何卸载已安装的技能？
A: 直接删除对应的技能目录即可：
```bash
rm -rf ~/.openclaw/skills/<skill-name>
```

### Q: 安装失败了怎么办？
A: 检查网络连接，然后重试。某些技能可能已被删除或移动。

### Q: 如何更新已安装的技能？
A: 重新运行安装命令会跳过已存在的技能。要更新，先删除旧版本再重新安装：
```bash
rm -rf ~/.openclaw/skills/<skill-name>
~/workspace/scripts/skills-update.sh install <skill-name>
```

## 技术细节

- 数据源: [awesome-openclaw-skills](https://github.com/VoltAgent/awesome-openclaw-skills)
- 技能来源: [openclaw/skills](https://github.com/openclaw/skills)
- 使用 GitHub API 下载技能文件
- 支持 curl 下载（无需额外依赖）

## 维护

定期运行同步命令以获取最新技能：

```bash
# 每周同步一次新技能
~/workspace/scripts/skills-update.sh sync 20
```

## 相关链接

- [awesome-openclaw-skills 仓库](https://github.com/VoltAgent/awesome-openclaw-skills)
- [openclaw/skills 仓库](https://github.com/openclaw/skills)
- [OpenClaw 官方文档](https://docs.openclaw.ai)
