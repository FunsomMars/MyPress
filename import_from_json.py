#!/usr/bin/env python
"""
Import posts from JSON file to Docker container
"""
import os
import sys
import json
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_press.settings.dev')
sys.path.insert(0, '/app')
django.setup()

import re
from urllib.parse import quote
from django.contrib.auth import get_user_model
from wagtail.models import Page, Site
from home.models import BlogPage, BlogIndexPage
from django.utils import timezone
from datetime import datetime

User = get_user_model()

def make_slug(post_name, post_id):
    """Generate slug"""
    if post_name:
        slug = post_name
    else:
        ascii_chars = re.findall(r'[a-zA-Z0-9]+', str(post_id))
        slug = f"post-{post_id}"
    
    slug = ''.join(c if c.isalnum() or c in '-_' else '-' for c in slug)
    slug = slug.strip('-')
    return slug[:50] if slug else f"post-{post_id}"

def clean_content(content):
    """Clean HTML content"""
    if not content:
        return ""
    
    # Replace WordPress image URLs
    content = content.replace('https://www.mspace.tech/wp-content/uploads', '/media')
    content = content.replace('http://www.mspace.tech/wp-content/uploads', '/media')
    
    # Clean escapes - more aggressive cleanup
    content = content.replace('\\r\\n', '').replace('\\n', '')
    content = content.replace('\r\n', '').replace('\n', '')
    content = content.replace('&nbsp;', ' ')
    content = content.replace('\\"', '"')
    content = content.replace("\\'", "'")
    
    # Remove HTML comments
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    
    # Fix escaped quotes around URLs
    content = re.sub(r'href=\\\"(/media/[^\"]+)\\\"', r'href="\1"', content)
    content = re.sub(r'src=\\\"(/media/[^\"]+)\\\"', r'src="\1"', content)
    content = content.replace('\\\"', '"')
    
    # Convert audio shortcode to HTML5 audio tag
    def replace_audio(match):
        url = match.group(1)
        preload = match.group(3) or 'auto'
        return f'<audio controls preload="{preload}" src="{url}" style="width:100%;margin:20px 0;"></audio>'
    content = re.sub(r'\[audio\s+mp3="([^"]+)"\s*(preload="([^"]+)")?\s*\]\[\/audio\]', replace_audio, content)
    
    # URL encode non-ASCII characters in media URLs
    def encode_url(match):
        url = match.group(1)
        if any(ord(c) > 127 for c in url):
            if '/' in url:
                path, filename = url.rsplit('/', 1)
                encoded = quote(filename, safe='')
                return match.group(0).replace(url, path + '/' + encoded)
        return match.group(0)
    content = re.sub(r'src="(/media/[^"]+)"', encode_url, content)
    content = re.sub(r'href="(/media/[^"]+)"', encode_url, content)
    
    return content

def import_posts(posts):
    """Import posts to Wagtail"""
    index = BlogIndexPage.objects.first()
    if not index:
        print("Cannot get blog index page")
        return 0
    
    imported = 0
    for post in posts:
        try:
            post_id = post['ID']
            title = post['title']
            content = post['content']
            post_date = post['date']
            post_name = post.get('slug', '')
            
            slug = make_slug(post_name, post_id)
            
            # Parse date
            if post_date:
                try:
                    pub_date = datetime.strptime(post_date, '%Y-%m-%d %H:%M:%S')
                    pub_date = timezone.make_aware(pub_date)
                except:
                    pub_date = timezone.now()
            else:
                pub_date = timezone.now()
            
            # Clean content
            content = clean_content(content)
            
            # Check if exists
            if BlogPage.objects.filter(slug=slug).exists():
                print(f"Skipping existing: {title[:50]}")
                continue
            
            # Create blog page
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
            print(f"Imported: {title[:50]}...")
            
        except Exception as e:
            import traceback
            print(f"Error importing '{post.get('title', 'Unknown')[:50]}': {e}")
            continue
    
    return imported

def main():
    print("=" * 50)
    print("Import posts from JSON")
    print("=" * 50)
    
    # Read JSON
    json_file = '/tmp/posts.json'
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        posts = json.load(f)
    
    print(f"Found {len(posts)} posts")
    
    if not posts:
        print("No posts to import")
        return
    
    # Import posts
    print("\nImporting posts...")
    count = import_posts(posts)
    
    print(f"\nSuccessfully imported {count} posts!")

if __name__ == '__main__':
    main()
