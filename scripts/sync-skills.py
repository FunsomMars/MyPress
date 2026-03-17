#!/usr/bin/env python3
"""
OpenClaw Skills Sync Script
从 awesome-openclaw-skills 仓库同步技能到本地技能库
"""

import os
import re
import json
import subprocess
import argparse
from pathlib import Path
from urllib.parse import urlparse
import shutil

# 配置
AWESOME_REPO_URL = "https://github.com/VoltAgent/awesome-openclaw-skills.git"
AWESOME_REPO_PATH = Path.home() / ".openclaw" / "workspace" / "temp_skills_repo"

# 安装位置：全局优先
SKILLS_INSTALL_PATH = Path.home() / ".openclaw" / "skills"
# 工作空间技能位置
WORKSPACE_SKILLS_PATH = Path.home() / ".openclaw" / "workspace" / "skills"

# 创建必要的目录
SKILLS_INSTALL_PATH.mkdir(parents=True, exist_ok=True)
WORKSPACE_SKILLS_PATH.mkdir(parents=True, exist_ok=True)


def clone_or_update_repo(repo_url, repo_path):
    """克隆或更新仓库"""
    if repo_path.exists():
        print(f"更新仓库: {repo_path.name}")
        subprocess.run(
            ["git", "-C", str(repo_path), "fetch", "origin"],
            check=True,
            capture_output=True,
            text=True
        )
        subprocess.run(
            ["git", "-C", str(repo_path), "reset", "--hard", "origin/main"],
            check=True,
            capture_output=True,
            text=True
        )
    else:
        print(f"克隆仓库: {repo_path.name}")
        subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(repo_path)],
            check=True,
            capture_output=True,
            text=True
        )


def parse_skill_links_from_md(md_file):
    """从 Markdown 文件中解析技能链接"""
    skills = []
    try:
        content = md_file.read_text(encoding='utf-8')
    except Exception as e:
        print(f"    警告: 无法读取文件 {md_file.name}: {e}")
        return skills

    # 匹配格式: - [skill-name](https://github.com/openclaw/skills/tree/main/skills/...)
    pattern = r'- \[([^\]]+)\]\((https://github\.com/openclaw/skills/tree/main/skills/[^\)]+/SKILL\.md)\)'

    matches = re.findall(pattern, content)

    for skill_name, skill_url in matches:
        # 从 URL 提取技能路径
        # 示例: https://github.com/openclaw/skills/tree/main/skills/mfergpt/4claw/SKILL.md
        url_path = urlparse(skill_url).path
        # path 应该是 /skills/mfergpt/4claw
        parts = [p for p in url_path.split('/') if p]  # 去掉空字符串

        # 查找 'tree' 的位置并跳过它
        if 'tree' in parts:
            tree_idx = parts.index('tree')
            parts = parts[tree_idx+1:]  # 从 tree 后面开始

        # 现在应该是 ['main', 'skills', 'mfergpt', '4claw', 'SKILL.md']
        # 跳过 'main'
        if parts and parts[0] == 'main':
            parts = parts[1:]

        # 现在应该是 ['skills', 'mfergpt', '4claw', 'SKILL.md']
        if len(parts) >= 4 and parts[0] == 'skills' and parts[-1] == 'SKILL.md':
            skill_path = '/'.join(parts[1:-1])  # mfergpt/4claw
            skills.append({
                'name': skill_name,
                'url': skill_url,
                'path': skill_path
            })

    return skills


def get_all_skills():
    """获取所有分类中的技能"""
    categories_dir = AWESOME_REPO_PATH / "categories"
    all_skills = []

    if not categories_dir.exists():
        print(f"警告: 分类目录不存在: {categories_dir}")
        return all_skills

    md_files = sorted(categories_dir.glob("*.md"))
    print(f"发现 {len(md_files)} 个分类文件")

    for md_file in md_files:
        category = md_file.stem
        skills = parse_skill_links_from_md(md_file)
        if skills:
            print(f"  {category}: {len(skills)} 个技能")
            all_skills.extend(skills)

    print(f"\n总计: {len(all_skills)} 个技能")
    return all_skills


def curl_download(url, output_path):
    """使用 curl 下载文件"""
    try:
        result = subprocess.run(
            ["curl", "-sSL", "-o", str(output_path), url],
            check=False,  # 不抛出异常，返回码自己判断
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            # 检查是否下载了有效内容
            if output_path.exists() and output_path.stat().st_size > 0:
                return True
        return False
    except Exception as e:
        return False


def download_skill_files(skill_path, dry_run=False):
    """从 GitHub 下载技能文件"""
    skill_name = skill_path.split('/')[-1]
    local_path = SKILLS_INSTALL_PATH / skill_name

    if local_path.exists():
        return f"✓ 已存在: {skill_name}"

    if dry_run:
        return f"[DRY-RUN] 将安装: {skill_name}"

    try:
        # 使用 GitHub API 获取技能目录的内容
        api_url = f"https://api.github.com/repos/openclaw/skills/contents/skills/{skill_path}"

        # 使用 curl 获取 API 响应
        result = subprocess.run(
            ["curl", "-sSL", api_url],
            check=False,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return f"✗ API 网络错误: {skill_name}"

        try:
            contents = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            return f"✗ JSON 解析失败: {skill_name} - {result.stdout[:100]}"

        # 如果是字符串，说明是单个文件
        if isinstance(contents, str):
            contents = json.loads(contents)

        # 创建本地目录
        local_path.mkdir(parents=True, exist_ok=True)

        # 下载所有文件
        file_count = 0
        for item in contents:
            if isinstance(item, dict) and item.get('type') == 'file':
                download_url = item.get('download_url')
                file_name = item.get('name')

                if download_url and file_name:
                    file_path = local_path / file_name
                    if curl_download(download_url, file_path):
                        file_count += 1

        # 检查是否成功下载了 SKILL.md
        if (local_path / "SKILL.md").exists():
            return f"✓ 安装成功: {skill_name}"
        else:
            shutil.rmtree(local_path, ignore_errors=True)
            return f"✗ 缺少 SKILL.md: {skill_name}"

    except subprocess.TimeoutExpired:
        return f"✗ 超时: {skill_name}"
    except Exception as e:
        # 清理可能的不完整安装
        if local_path.exists():
            shutil.rmtree(local_path, ignore_errors=True)
        return f"✗ 安装失败: {skill_name} - {e}"


def sync_skills(skill_filter=None, dry_run=False, limit=None, category=None):
    """同步技能到本地"""
    print("=" * 60)
    print("OpenClaw Skills Sync")
    print("=" * 60)

    # 1. 克隆或更新 awesome 列表仓库
    clone_or_update_repo(AWESOME_REPO_URL, AWESOME_REPO_PATH)

    # 2. 获取所有技能
    all_skills = get_all_skills()

    if not all_skills:
        print("未发现任何技能")
        return

    # 3. 过滤技能
    if skill_filter:
        all_skills = [s for s in all_skills if skill_filter.lower() in s['name'].lower()]
        print(f"\n按名称过滤 '{skill_filter}': {len(all_skills)} 个技能")

    if limit:
        all_skills = all_skills[:limit]
        print(f"限制数量: {len(all_skills)} 个技能")

    print(f"\n准备安装 {len(all_skills)} 个技能到: {SKILLS_INSTALL_PATH}")
    if dry_run:
        print("⚠️  DRY RUN 模式 - 不会实际安装")

    # 4. 安装技能
    success = 0
    failed = 0
    skipped = 0

    for skill in all_skills:
        result = download_skill_files(skill['path'], dry_run)
        if result.startswith("✓ 已存在"):
            skipped += 1
        elif result.startswith("✓"):
            success += 1
        else:
            failed += 1
        print(f"  {result}")

    # 5. 总结
    print("\n" + "=" * 60)
    print("同步完成")
    print(f"  成功: {success}")
    print(f"  跳过: {skipped}")
    print(f"  失败: {failed}")
    print(f"  总计: {len(all_skills)}")
    print("=" * 60)


def list_installed_skills():
    """列出已安装的技能"""
    print("已安装的技能:")
    print("-" * 60)

    if SKILLS_INSTALL_PATH.exists():
        count = 0
        for skill_dir in sorted(SKILLS_INSTALL_PATH.iterdir()):
            if skill_dir.is_dir():
                count += 1
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    # 读取第一行作为描述
                    try:
                        lines = skill_md.read_text(encoding='utf-8').split('\n')
                        title = lines[0].strip('# ') if lines else ''
                        desc = lines[1].strip() if len(lines) > 1 else ''
                        if title:
                            print(f"  {skill_dir.name}")
                            print(f"    {title}")
                            if desc:
                                print(f"    {desc[:60]}..." if len(desc) > 60 else f"    {desc}")
                    except:
                        print(f"  {skill_dir.name}")
                        print(f"    (无法读取描述)")
                else:
                    print(f"  {skill_dir.name} (无 SKILL.md)")
        print(f"\n总计: {count} 个技能")
    else:
        print("  未安装任何技能")


def search_skills(query):
    """搜索可用技能"""
    print(f"搜索 '{query}':")
    print("-" * 60)

    clone_or_update_repo(AWESOME_REPO_URL, AWESOME_REPO_PATH)

    all_skills = get_all_skills()
    filtered = [s for s in all_skills if query.lower() in s['name'].lower()]

    if filtered:
        print(f"找到 {len(filtered)} 个匹配的技能:\n")
        for skill in filtered[:20]:  # 限制显示数量
            print(f"  • {skill['name']}")
            print(f"    路径: {skill['path']}")
            print()

        if len(filtered) > 20:
            print(f"... 还有 {len(filtered) - 20} 个结果")
    else:
        print("未找到匹配的技能")


def main():
    parser = argparse.ArgumentParser(
        description="同步 OpenClaw 技能库",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --sync              同步所有技能
  %(prog)s --sync --limit 10   同步前 10 个技能
  %(prog)s --sync --filter "ai" 同步名称包含 "ai" 的技能
  %(prog)s --search "weather"  搜索可用技能
  %(prog)s --list              列出已安装技能
        """
    )
    parser.add_argument("--sync", action="store_true", help="同步技能")
    parser.add_argument("--list", "-l", action="store_true", help="列出已安装技能")
    parser.add_argument("--search", "-s", help="搜索可用技能")
    parser.add_argument("--filter", "-f", help="按名称过滤技能")
    parser.add_argument("--limit", "-n", type=int, help="限制安装数量")
    parser.add_argument("--dry-run", "-d", action="store_true", help="模拟运行，不实际安装")

    args = parser.parse_args()

    if args.search:
        search_skills(args.search)
    elif args.list:
        list_installed_skills()
    elif args.sync:
        sync_skills(
            skill_filter=args.filter,
            dry_run=args.dry_run,
            limit=args.limit
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
