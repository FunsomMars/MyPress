#!/usr/bin/env python
"""
修复博客文章中的图片显示
将本地图片导入到Wagtail并替换文章中的URL
"""
import os
import sys
import re
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_press.settings.dev')
django.setup()

from django.contrib.auth import get_user_model
from wagtail.models import Page
from home.models import BlogPage, BlogIndexPage
from wagtail.images import get_image_model
from django.core.files.base import ContentFile
from PIL import Image as PILImage
import hashlib

Image = get_image_model()

# 图片存储目录
LOCAL_UPLOADS_PATH = '/Users/mars/Documents/Coding/my_press/data/uploads'
ORIGINAL_IMAGES_PATH = '/Users/mars/Documents/Coding/my_press/media/original_images'

def find_image_by_filename(filename):
    """尝试在多个位置查找图片"""
    if not filename:
        return None
    
    # 提取基础名
    base_name = os.path.basename(filename).split('?')[0]
    
    # 1. 尝试在original_images目录 (精确匹配)
    original_path = os.path.join(ORIGINAL_IMAGES_PATH, base_name)
    if os.path.exists(original_path):
        return original_path
    
    # 2. 在original_images目录中查找带哈希值的文件
    name_without_ext = os.path.splitext(base_name)[0]
    ext = os.path.splitext(base_name)[1]
    
    if os.path.exists(ORIGINAL_IMAGES_PATH):
        for f in os.listdir(ORIGINAL_IMAGES_PATH):
            # 检查是否以base_name的主名前缀开头
            f_name = os.path.splitext(f)[0]
            if f_name.startswith(name_without_ext[:15]) or name_without_ext.startswith(f_name[:15]):
                return os.path.join(ORIGINAL_IMAGES_PATH, f)
    
    # 3. 尝试在uploads目录中查找
    for root, dirs, files in os.walk(LOCAL_UPLOADS_PATH):
        if base_name in files:
            return os.path.join(root, base_name)
    
    # 4. 尝试前缀匹配
    for root, dirs, files in os.walk(LOCAL_UPLOADS_PATH):
        for f in files:
            f_base = os.path.splitext(f)[0]
            if f_base.startswith(name_without_ext[:10]):
                return os.path.join(root, f)
    
    return None

def import_single_image(filename):
    """导入单张图片到Wagtail"""
    if not filename:
        return None
    
    # 提取基础文件名
    base_filename = os.path.basename(filename.split('?')[0])
    
    # 检查是否已存在
    existing = Image.objects.filter(title=base_filename).first()
    if existing:
        return existing.file.url
    
    # 查找本地文件
    local_path = find_image_by_filename(base_filename)
    if not local_path:
        return None
    
    print(f"    找到图片: {os.path.basename(local_path)}")
    
    try:
        # 获取图片尺寸
        width, height = 800, 600
        try:
            with PILImage.open(local_path) as pil_img:
                width, height = pil_img.size
                print(f"    尺寸: {width}x{height}")
        except Exception as e:
            print(f"    无法读取尺寸: {e}")
        
        # 创建Wagtail图片 - 先保存文件，再设置尺寸
        img = Image()
        img.title = os.path.basename(local_path)
        
        with open(local_path, 'rb') as f:
            file_content = f.read()
        
        # 先保存文件（不设置width/height）
        img.file.save(os.path.basename(local_path), ContentFile(file_content), save=True)
        
        # 然后设置尺寸并保存
        img.width = width
        img.height = height
        img.save()
        
        print(f"    ✅ 成功导入")
        return img.file.url
        
    except Exception as e:
        import traceback
        print(f"    ❌ 导入失败: {e}")
        return None

def process_post_images(blog_page):
    """处理单篇文章中的图片"""
    # 获取文章内容
    content = str(blog_page.body)
    
    # 查找所有原站图片URL
    image_urls = re.findall(r'https?://www\.mspace\.tech/wp-content/uploads/[^"\'<>\s]+', content)
    
    if not image_urls:
        return
    
    # 去重
    image_urls = list(set(image_urls))
    print(f"  处理 {len(image_urls)} 张图片...")
    
    updated = False
    for url in image_urls:
        filename = os.path.basename(url.split('?')[0])
        
        # 尝试导入图片
        local_url = import_single_image(filename)
        
        if local_url:
            content = content.replace(url, local_url)
            updated = True
    
    # 更新文章内容
    if updated:
        blog_page.body = content
        blog_page.save()
        print(f"  已更新文章")

def main():
    print("=" * 50)
    print("修复博客文章图片")
    print("=" * 50)
    
    # 获取所有博客文章
    posts = BlogPage.objects.all()
    print(f"\n找到 {posts.count()} 篇文章")
    
    for post in posts:
        print(f"\n处理: {post.title[:30]}...")
        process_post_images(post)
    
    print("\n✅ 完成!")

if __name__ == '__main__':
    main()
