#!/usr/bin/env python
"""
WordPress to Wagtail Migration Script
将WordPress数据导入到Wagtail CMS
从本地uploads文件夹读取图片
"""
import os
import sys
import re
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_press.settings.dev')
django.setup()

from django.contrib.auth import get_user_model
from wagtail.models import Page, Site
from home.models import BlogPage, BlogIndexPage
from wagtail.fields import RichTextField
from wagtail.images.models import Image
from wagtail.images import get_image_model
from django.utils import timezone
from datetime import datetime
from django.core.files.base import ContentFile
import hashlib
from PIL import Image as PILImage

User = get_user_model()

# 本地图片文件夹路径
LOCAL_UPLOADS_PATH = '/Users/mars/Documents/Coding/my_press/data/uploads'

def find_local_image(filename):
    """从本地uploads文件夹查找图片"""
    if not filename:
        return None
    
    # 遍历所有年份文件夹
    for root, dirs, files in os.walk(LOCAL_UPLOADS_PATH):
        if filename in files:
            return os.path.join(root, filename)
    
    # 如果找不到，尝试模糊匹配
    name_without_ext = os.path.splitext(filename)[0]
    for root, dirs, files in os.walk(LOCAL_UPLOADS_PATH):
        for f in files:
            if f.startswith(name_without_ext):
                return os.path.join(root, f)
    
    return None

def process_content_images(content, post_id, post_title):
    """处理文章内容中的图片，从本地查找并创建Image对象"""
    # 找到所有原站图片URL
    image_urls = re.findall(r'https?://www\.mspace\.tech/wp-content/uploads/[^"\'<>\s]+', content)
    
    if not image_urls:
        return content
    
    # 去重
    image_urls = list(set(image_urls))
    print(f"  发现 {len(image_urls)} 张图片")
    
    Image = get_image_model()
    processed_count = 0
    
    for url in image_urls:
        try:
            # 从URL提取文件名
            filename = os.path.basename(url.split('?')[0])
            
            # 尝试从本地找到图片
            local_path = find_local_image(filename)
            
            if local_path:
                # 相对路径
                relative_path = os.path.relpath(local_path, '/Users/mars/Documents/Coding/my_press/media')
                
                # 检查图片是否已存在
                existing = Image.objects.filter(file=relative_path).first()
                if existing:
                    content = content.replace(url, existing.file.url)
                    continue
                
                # 使用PIL获取图片尺寸
                try:
                    with PILImage.open(local_path) as pil_img:
                        width, height = pil_img.size
                except:
                    width, height = 800, 600  # 默认尺寸
                
                # 创建Wagtail Image对象
                image = Image()
                image.title = os.path.basename(filename)
                image.width = width
                image.height = height
                with open(local_path, 'rb') as f:
                    image.file.save(
                        os.path.basename(filename),
                        ContentFile(f.read()),
                        save=True
                    )
                image.save()
                
                # 替换内容中的URL
                content = content.replace(url, image.file.url)
                processed_count += 1
                print(f"    ✅ 已处理: {os.path.basename(filename)} ({width}x{height})")
            else:
                print(f"    ❌ 本地未找到: {filename}")
                
        except Exception as e:
            print(f"  处理图片失败: {e}")
            continue
    
    print(f"  成功处理 {processed_count}/{len(image_urls)} 张图片")
    return content

def parse_wp_posts(sql_file):
    """解析WordPress posts SQL文件"""
    posts = []
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到INSERT INTO wp_posts VALUES ...行
    pattern = r"INSERT INTO `wp_posts` VALUES\s*\((.+)\);"
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("未找到wp_posts数据")
        return posts
    
    values_content = match.group(1)
    
    # 用 ),( 分割记录
    raw_records = values_content.split('),(')
    
    # 修复第一个和最后一个
    records = []
    for i, raw in enumerate(raw_records):
        if i == 0:
            record = '(' + raw
        elif i == len(raw_records) - 1:
            record = raw + ')'
        else:
            record = '(' + raw + ')'
        
        if record.strip():
            records.append(record)
    
    print(f"找到 {len(records)} 条记录")
    
    for record in records:
        try:
            parts = record.split(',')
            
            if len(parts) < 21:
                continue
            
            post_id = parts[0].strip()
            post_date = parts[2].strip().strip("'") if len(parts) > 2 else ''
            post_content = parts[4].strip().strip("'") if len(parts) > 4 else ''
            post_title = parts[5].strip().strip("'") if len(parts) > 5 else ''
            post_status = parts[7].strip().strip("'") if len(parts) > 7 else ''
            post_type = parts[20].strip().strip("'") if len(parts) > 20 else ''
            
            if post_type != 'post' or post_status != 'publish':
                continue
            
            if post_title and post_title != '':
                posts.append({
                    'id': post_id,
                    'title': post_title,
                    'content': post_content,
                    'date': post_date
                })
                
        except Exception as e:
            print(f"解析记录出错: {e}")
            continue
    
    print(f"过滤后找到 {len(posts)} 篇已发布的文章")
    return posts

def make_slug(title, post_id):
    """从标题生成合法的slug"""
    import re
    ascii_chars = re.findall(r'[a-zA-Z0-9]+', title)
    
    if ascii_chars:
        base = ascii_chars[0].lower()
    else:
        base = 'post'
    
    slug = f"{base}-{post_id}"
    slug = ''.join(c if c.isalnum() or c in '-_' else '-' for c in slug)
    slug = slug.strip('-')
    
    return slug[:50] if slug else f"post-{post_id}"

def import_posts(posts):
    """导入文章到Wagtail"""
    index = BlogIndexPage.objects.first()
    if not index:
        print("无法获取博客索引")
        return
    
    imported = 0
    for post in posts:
        try:
            title = post['title']
            post_id = post.get('id', str(imported))
            
            slug = make_slug(title, post_id)
            
            # 解析日期
            pub_date = timezone.now()
            if post.get('date'):
                try:
                    pub_date = datetime.strptime(post['date'], '%Y-%m-%d %H:%M:%S')
                    pub_date = timezone.make_aware(pub_date)
                except:
                    pass
            
            # 清理HTML内容
            content = post['content']
            content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
            content = content.replace('\\r\\n', '\n').replace('\\n', '\n')
            content = content.replace('&nbsp;', ' ')
            content = content.replace('\\"', '"')
            content = content.replace("\\'", "'")
            content = content[:50000]  # 限制长度
            
            # 处理图片 - 从本地查找并替换URL
            print(f"处理图片: {title[:30]}...")
            content = process_content_images(content, post_id, title)
            
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
            print(f"Error importing '{post.get('title', 'Unknown')[:30]}': {e}")
            continue
    
    print(f"\n✅ 成功导入 {imported} 篇文章!")

def main():
    print("=" * 50)
    print("WordPress to Wagtail 迁移工具 (本地图片)")
    print("=" * 50)
    
    # 检查本地图片文件夹
    if not os.path.exists(LOCAL_UPLOADS_PATH):
        print(f"错误: 找不到本地图片文件夹 {LOCAL_UPLOADS_PATH}")
        return
    
    # 检查数据文件
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    posts_file = os.path.join(data_dir, 'wordpress_posts.sql')
    
    if not os.path.exists(posts_file):
        print(f"错误: 找不到数据文件 {posts_file}")
        return
    
    # 解析文章
    print("\n📄 正在解析WordPress文章...")
    posts = parse_wp_posts(posts_file)
    print(f"找到 {len(posts)} 篇文章")
    
    if not posts:
        print("没有找到可导入的文章")
        return
    
    # 导入文章
    print("\n📥 正在导入文章到Wagtail (使用本地图片)...")
    import_posts(posts)
    
    print("\n✨ 迁移完成!")

if __name__ == '__main__':
    main()
