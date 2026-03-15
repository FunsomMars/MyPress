#!/usr/bin/env python
"""
Import pages from JSON file to Docker container
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
from django.contrib.auth import get_user_model
from wagtail.models import Page
from home.models import HomePage, CustomPage
from django.utils import timezone
from datetime import datetime

User = get_user_model()

def make_slug(post_name, post_id):
    """Generate slug"""
    if post_name:
        slug = post_name
    else:
        slug = f"page-{post_id}"
    
    slug = ''.join(c if c.isalnum() or c in '-_' else '-' for c in slug)
    slug = slug.strip('-')
    return slug[:50] if slug else f"page-{post_id}"

def clean_content(content):
    """Clean HTML content"""
    if not content:
        return ""
    
    # Replace WordPress image URLs
    content = content.replace('https://www.mspace.tech/wp-content/uploads', '/media')
    content = content.replace('http://www.mspace.tech/wp-content/uploads', '/media')
    content = content.replace('https://www.mspace.tech/wp-content', '/media')
    content = content.replace('http://www.mspace.tech/wp-content', '/media')
    
    # Clean escapes
    content = content.replace('\\r\\n', '\n').replace('\\n', '\n')
    content = content.replace('&nbsp;', ' ')
    content = content.replace('\\"', '"')
    content = content.replace("\\'", "'")
    
    # Remove HTML comments
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    
    return content

def import_pages(pages):
    """Import pages to Wagtail"""
    home = HomePage.objects.first()
    if not home:
        print("Cannot get home page")
        return 0
    
    imported = 0
    for page in pages:
        try:
            post_id = page['ID']
            title = page['title']
            content = page['content']
            post_date = page['date']
            post_name = page.get('slug', '')
            
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
            if CustomPage.objects.filter(slug=slug).exists():
                print(f"Skipping existing: {title[:50]}")
                continue
            
            # Create custom page
            custom_page = CustomPage(
                title=title[:255],
                slug=slug[:255],
                body=content,
                intro=title[:100]
            )
            
            home.add_child(instance=custom_page)
            
            revision = custom_page.save_revision()
            revision.publish()
            
            imported += 1
            print(f"Imported: {title[:50]}...")
            
        except Exception as e:
            import traceback
            print(f"Error importing '{page.get('title', 'Unknown')[:50]}': {e}")
            continue
    
    return imported

def main():
    print("=" * 50)
    print("Import pages from JSON")
    print("=" * 50)
    
    # Read JSON
    json_file = '/tmp/pages.json'
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found")
        return
    
    with open(json_file, 'r', encoding='utf-8') as f:
        pages = json.load(f)
    
    print(f"Found {len(pages)} pages")
    
    if not pages:
        print("No pages to import")
        return
    
    # Import pages
    print("\nImporting pages...")
    count = import_pages(pages)
    
    print(f"\nSuccessfully imported {count} pages!")

if __name__ == '__main__':
    main()
