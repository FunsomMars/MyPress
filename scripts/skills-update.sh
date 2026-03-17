#!/bin/bash
# 快捷脚本：更新技能库
# 用法: ./skills-update.sh [选项]
#
# 示例:
#   ./skills-update.sh              # 查看帮助
#   ./skills-update.sh sync         # 同步所有技能
#   ./skills-update.sh sync 10      # 同步前 10 个技能
#   ./skills-update.sh search ai    # 搜索 "ai" 相关技能
#   ./skills-update.sh list         # 列出已安装技能
#   ./skills-update.sh install git  # 安装名称包含 "git" 的技能

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC_SCRIPT="$SCRIPT_DIR/sync-skills.py"

case "$1" in
    sync)
        # 同步技能，可指定数量
        if [[ -n "$2" && "$2" =~ ^[0-9]+$ ]]; then
            python3 "$SYNC_SCRIPT" --sync --limit "$2"
        elif [[ -n "$2" ]]; then
            python3 "$SYNC_SCRIPT" --sync --filter "$2"
        else
            echo "⚠️  同步所有技能需要很长的 时间！"
            echo "使用 --limit 或 --filter 选项来限制数量。"
            echo ""
            echo "示例:"
            echo "  $0 sync 10           # 同步前 10 个技能"
            echo "  $0 sync weather     # 同步名称包含 'weather' 的技能"
            echo ""
            read -p "确定要同步所有 5409 个技能吗？(yes/no): " confirm
            if [[ "$confirm" == "yes" ]]; then
                python3 "$SYNC_SCRIPT" --sync
            fi
        fi
        ;;
    search)
        # 搜索技能
        if [[ -n "$2" ]]; then
            python3 "$SYNC_SCRIPT" --search "$2"
        else
            echo "用法: $0 search <关键词>"
        fi
        ;;
    list)
        # 列出已安装技能
        python3 "$SYNC_SCRIPT" --list
        ;;
    install)
        # 安装指定名称的技能
        if [[ -n "$2" ]]; then
            python3 "$SYNC_SCRIPT" --sync --filter "$2"
        else
            echo "用法: $0 install <技能名称>"
            echo "示例: $0 install weather"
        fi
        ;;
    test)
        # 测试模式（dry-run）
        python3 "$SYNC_SCRIPT" --sync --limit 3 --dry-run
        ;;
    *)
        echo "OpenClaw 技能库管理工具"
        echo ""
        echo "用法: $0 <命令> [参数]"
        echo ""
        echo "命令:"
        echo "  sync [数量|名称]   同步技能（所有、指定数量或按名称过滤）"
        echo "  search <关键词>    搜索可用技能"
        echo "  list              列出已安装的技能"
        echo "  install <名称>     安装指定名称的技能"
        echo "  test              测试运行（模拟，不实际安装）"
        echo ""
        echo "示例:"
        echo "  $0 sync 10                    # 同步前 10 个技能"
        echo "  $0 sync weather               # 安装 weather 相关技能"
        echo "  $0 search ai                  # 搜索 AI 相关技能"
        echo "  $0 list                      # 查看已安装的技能"
        echo "  $0 install git                # 安装 git 相关技能"
        ;;
esac
