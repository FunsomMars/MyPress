"""
Management command to automatically initialize blog pages.
Runs on each app startup to ensure required pages exist.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from wagtail.models import Page
from home.models import HomePage, BlogIndexPage, CustomPage, BlogPage


class Command(BaseCommand):
    help = 'Initialize blog pages and data'

    def handle(self, *args, **options):
        self.stdout.write('Starting page initialization...')
        
        # 1. Ensure HomePage exists
        home = HomePage.objects.first()
        if not home:
            # Get root page
            root = Page.objects.get(depth=1)
            home = HomePage(
                title='Home',
                slug='home',
            )
            root.add_child(instance=home)
            self.stdout.write(self.style.SUCCESS('✓ Created HomePage'))
        else:
            self.stdout.write('HomePage already exists')
        
        # 2. Ensure BlogIndexPage exists
        blog_index = BlogIndexPage.objects.first()
        if not blog_index:
            blog_index = BlogIndexPage(
                title='Blog',
                slug='blog',
            )
            home.add_child(instance=blog_index)
            
            # Save revision and publish
            revision = blog_index.save_revision()
            revision.publish()
            self.stdout.write(self.style.SUCCESS('✓ Created BlogIndexPage'))
        else:
            self.stdout.write('BlogIndexPage already exists')
        
        # 3. Ensure custom pages exist
        existing_slugs = ['essay', 'about', 'video', 'music', 'linux', 'jokes', 'files', 'concept', 'privacy']
        existing_custom = CustomPage.objects.filter(slug__in=existing_slugs)
        existing_slugs_in_db = list(existing_custom.values_list('slug', flat=True))
        
        # Default page titles (can be translated later)
        page_titles = {
            'essay': 'Essays',
            'about': 'About',
            'video': 'Videos',
            'music': 'Music',
            'linux': 'Linux',
            'jokes': 'Jokes',
            'files': 'Files',
            'concept': 'Concepts',
            'privacy': 'Privacy Policy',
        }
        
        created_count = 0
        for slug, title in page_titles.items():
            if slug not in existing_slugs_in_db:
                custom_page = CustomPage(
                    title=title,
                    slug=slug,
                    intro=f'{title} content',
                    body=f'<p>Welcome to {title}</p>',
                )
                home.add_child(instance=custom_page)
                
                # Save revision and publish
                revision = custom_page.save_revision()
                revision.publish()
                
                created_count += 1
                self.stdout.write(f'✓ Created page: {title} ({slug})')
        
        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f'Created {created_count} custom pages'))
        else:
            self.stdout.write('Custom pages already exist')
        
        self.stdout.write(self.style.SUCCESS('Page initialization complete!'))
        
        # 4. Import posts (if they don't exist)
        import json
        import os
        from datetime import datetime
        posts_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'data', 'posts.json')
        
        if os.path.exists(posts_file):
            try:
                with open(posts_file, 'r', encoding='utf-8') as f:
                    posts_data = json.load(f)
                
                existing_slugs = list(BlogPage.objects.values_list('slug', flat=True))
                
                for post in posts_data:
                    slug = post.get('slug', '')
                    if slug and slug not in existing_slugs:
                        # Parse date
                        date_value = post.get('date')
                        if date_value:
                            try:
                                # Try to parse date
                                if isinstance(date_value, str):
                                    # Remove time part, keep only date
                                    date_str = date_value.split(' ')[0]
                                    article_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                                else:
                                    article_date = date_value
                            except:
                                article_date = timezone.now().date()
                        else:
                            article_date = timezone.now().date()
                        
                        blog_page = BlogPage(
                            title=post.get('title', 'Untitled'),
                            slug=slug,
                            intro=post.get('intro', post.get('title', '')[:100]),
                            body=post.get('content', ''),
                            date=article_date
                        )
                        blog_index.add_child(instance=blog_page)
                        
                        revision = blog_page.save_revision()
                        revision.publish()
                        
                        self.stdout.write(f'✓ Imported post: {post.get("title", "Untitled")}')
                
                self.stdout.write(self.style.SUCCESS('Post import complete!'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error importing posts: {e}'))
        else:
            self.stdout.write('posts.json not found, skipping post import')
