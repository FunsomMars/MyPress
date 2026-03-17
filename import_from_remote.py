#!/usr/bin/env python
"""
Direct WordPress Import Script
从远程WordPress MySQL数据库直接读取并导入文章
"""
import os
import sys
import django
import re

# Setup Django - use dev settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_press.settings.dev')

# Add /app to path for Docker
sys.path.insert(0, '/app')

django.setup()

import pymysql
from django.contrib.auth import get_user_model
from wagtail.models import Page, Site
from home.models import BlogPage, BlogIndexPage
from django.utils import timezone
from datetime import datetime

User = get_user_model()

# WordPress数据库配置
WP_CONFIG = {
    'host': '23.105.198.164',
    'user': 'wordpress',
    'password': 'mss15656132163',
    'database': 'wordpress',
    'charset': 'utf8mb4'
}

def get_wp_posts(limit=100):
    """从WordPress数据库获取文章"""
    conn = pymysql.connect(**WP_CONFIG)
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
                SELECT ID, post_title, post_content, post_date, post_status, post_type, post_name
                FROM wp_posts
                WHERE post_type = 'post' AND post_status = 'publish'
                ORDER BY ID DESC
                LIMIT %s
            """
            cursor.execute(sql, (limit,))
            return cursor.fetchall()
    finally:
        conn.close()

def make_slug(post_name, post_id):
    """生成slug"""
    if post_name:
        slug = post_name
    else:
        # 从标题生成slug
        import re
        ascii_chars = re.findall(r'[a-zA-Z0-9]+', str(post_id))
        slug = f"post-{post_id}"
    
    # 清理slug
    slug = ''.join(c if c.isalnum() or c in '-_' else '-' for c in slug)
    slug = slug.strip('-')
    return slug[:50] if slug else f"post-{post_id}"

def clean_content(content):
    """清理HTML内容"""
    if not content:
        return ""
    
    # 替换WordPress图片URL为新站URL
    content = content.replace('https://www.mspace.tech/wp-content/uploads', '/media')
    content = content.replace('http://www.mspace.tech/wp-content/uploads', '/media')
    
    # 清理转义
    content = content.replace('\\r\\n', '\n').replace('\\n', '\n')
    content = content.replace('&nbsp;', ' ')
    content = content.replace('\\"', '"')
    content = content.replace("\\'", "'")
    
    # 移除HTML注释
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    
    return content

def import_posts(posts):
    """导入文章到Wagtail"""
    index = BlogIndexPage.objects.first()
    if not index:
        print("无法获取博客索引页面")
        return 0
    
    imported = 0
    for post in posts:
        try:
            post_id = post['ID']
            title = post['post_title']
            content = post['post_content']
            post_date = post['post_date']
            post_name = post['post_name']
            
            # 生成slug
            slug = make_slug(post_name, post_id)
            
            # 解析日期
            if isinstance(post_date, datetime):
                pub_date = post_date
            else:
                pub_date = datetime.strptime(str(post_date), '%Y-%m-%d %H:%M:%S')
                pub_date = timezone.make_aware(pub_date)
            
            # 清理内容
            content = clean_content(content)
            
            # 检查是否已存在
            if BlogPage.objects.filter(slug=slug).exists():
                print(f"跳过已存在: {title[:50]}")
                continue
            
            # 创建博客页面
            blog_page = BlogPage(
                title=title[:255],
                slug=slug[:255],
                date=pub_date,
                body=content,
                intro=title[:100]
            )
            
            index.add_child(instance=blog_page)
            
            revision = blog_page.save_revision()
            revision.publish()
            
            imported += 1
            print(f"已导入: {title[:50]}...")
            
        except Exception as e:
            import traceback
            print(f"Error: {e}")
            continue
    
    return imported

def main():
    print("=" * 50)
    print("从远程WordPress数据库导入文章")
    print("=" * 50)
    
    # 获取文章
    print("\n📄 正在从WordPress获取文章...")
    posts = get_wp_posts(limit=200)
    print(f"找到 {len(posts)} 篇文章")
    
    if not posts:
        print("没有找到可导入的文章")
        return
    
    # 导入文章
    print("\n📥 正在导入文章...")
    count = import_posts(posts)
    
    print(f"\n✅ 成功导入 {count} 篇文章!")

if __name__ == '__main__':
    main()
