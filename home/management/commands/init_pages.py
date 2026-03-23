"""
自动初始化博客页面的管理命令
在每次应用启动时运行，确保必要的页面存在
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from wagtail.models import Page
from home.models import HomePage, BlogIndexPage, CustomPage, BlogPage


class Command(BaseCommand):
    help = '初始化博客页面和数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化页面...')
        
        # 1. 确保HomePage存在
        home = HomePage.objects.first()
        if not home:
            # 获取root page
            root = Page.objects.get(depth=1)
            home = HomePage(
                title='Home',
                slug='home',
            )
            root.add_child(instance=home)
            self.stdout.write(self.style.SUCCESS('✓ 创建了HomePage'))
        else:
            self.stdout.write('HomePage已存在')
        
        # 2. 确保BlogIndexPage存在
        blog_index = BlogIndexPage.objects.first()
        if not blog_index:
            blog_index = BlogIndexPage(
                title='Blog',
                slug='blog',
            )
            home.add_child(instance=blog_index)
            
            # 保存版本并发布
            revision = blog_index.save_revision()
            revision.publish()
            self.stdout.write(self.style.SUCCESS('✓ 创建了BlogIndexPage'))
        else:
            self.stdout.write('BlogIndexPage已存在')
        
        # 3. 确保自定义页面存在
        existing_slugs = ['essay', 'about', 'video', 'music', 'linux', 'jokes', 'files', 'concept', 'privacy']
        existing_custom = CustomPage.objects.filter(slug__in=existing_slugs)
        existing_slugs_in_db = list(existing_custom.values_list('slug', flat=True))
        
        page_titles = {
            'essay': '日常随笔',
            'about': '关于小孟',
            'video': '视频剪辑',
            'music': '云音乐歌单',
            'linux': '学点Linux',
            'jokes': '段子手段子',
            'files': '文件管理',
            'concept': '学点概念',
            'privacy': '隐私政策',
        }
        
        created_count = 0
        for slug, title in page_titles.items():
            if slug not in existing_slugs_in_db:
                custom_page = CustomPage(
                    title=title,
                    slug=slug,
                    intro=f'{title}相关内容',
                    body=f'<p>欢迎访问{title}页面</p>',
                )
                home.add_child(instance=custom_page)
                
                # 保存版本并发布
                revision = custom_page.save_revision()
                revision.publish()
                
                created_count += 1
                self.stdout.write(f'✓ 创建了页面: {title} ({slug})')
        
        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f'共创建了 {created_count} 个自定义页面'))
        else:
            self.stdout.write('自定义页面已存在')
        
        self.stdout.write(self.style.SUCCESS('页面初始化完成!'))
        
        # 4. 导入文章（如果文章不存在）
        import json
        import os
        from datetime import datetime
        posts_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'data', 'posts.json')
        
        if os.path.exists(posts_file):
            try:
                with open(posts_file, 'r', encoding='utf-8') as f:
                    posts_data = json.load(f)
                
                existing_slugs = set(BlogPage.objects.values_list('slug', flat=True))
                existing_titles = set(BlogPage.objects.values_list('title', flat=True))

                for post in posts_data:
                    slug = post.get('slug', '')
                    title = post.get('title', 'Untitled')
                    if slug and slug not in existing_slugs and title not in existing_titles:
                        # 处理日期格式
                        date_value = post.get('date')
                        if date_value:
                            try:
                                # 尝试解析日期
                                if isinstance(date_value, str):
                                    # 去除时间部分，只保留日期
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
                        
                        self.stdout.write(f'✓ 导入了文章: {post.get("title", "Untitled")}')
                
                self.stdout.write(self.style.SUCCESS('文章导入完成!'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'导入文章时出错: {e}'))
        else:
            self.stdout.write('未找到posts.json文件，跳过文章导入')
