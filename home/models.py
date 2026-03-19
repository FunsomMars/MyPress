from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
import uuid


class EmailVerification(models.Model):
    """邮箱验证模型"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='email_verification'
    )
    verification_code = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        verbose_name = "邮箱验证"
        verbose_name_plural = "邮箱验证"
    
    def __str__(self):
        return f"{self.user.email} - 验证"
    
    def is_valid(self):
        """检查验证码是否有效"""
        return timezone.now() < self.expires_at
    
    @staticmethod
    def create_for_user(user):
        """为用户创建验证记录"""
        from django.utils import timezone
        from datetime import timedelta
        
        # 删除旧的验证记录
        EmailVerification.objects.filter(user=user).delete()
        
        # 创建新的验证记录，24小时有效
        verification = EmailVerification.objects.create(
            user=user,
            verification_code=uuid.uuid4().hex,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        return verification


class GroupApplication(models.Model):
    """用户组申请模型"""
    STATUS_CHOICES = [
        ('pending', '待审批'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='group_applications'
    )
    requested_group = models.CharField(max_length=100)  # Editors, Moderators
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_applications'
    )
    review_note = models.TextField(blank=True)  # 审批备注
    
    class Meta:
        verbose_name = "用户组申请"
        verbose_name_plural = "用户组申请"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} -> {self.requested_group} ({self.status})"


class HomePage(Page):
    intro = RichTextField(blank=True, help_text="Introduction text for the homepage")
    template = 'home/index.html'
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]
    
    def get_context(self, request, *args, **kwargs):
        """获取博客文章列表上下文"""
        context = super().get_context(request, *args, **kwargs)
        # 获取博客索引页面的文章
        from home.models import BlogIndexPage
        blog_index = BlogIndexPage.objects.first()
        if blog_index:
            # 获取所有文章
            posts = list(blog_index.get_children().specific().live())
            # 按日期倒序排列
            def sort_key(post):
                if hasattr(post, 'date') and post.date:
                    return post.date
                elif hasattr(post, 'first_published_at') and post.first_published_at:
                    return post.first_published_at
                return post.pk
            posts.sort(key=sort_key, reverse=True)
            # 取前6篇（最新的6篇）
            context['blog_posts'] = posts[:6]
        else:
            context['blog_posts'] = []
        return context


class BlogIndexPage(Page):
    """博客索引页面 - 显示文章列表"""
    intro = RichTextField(blank=True, help_text="Introduction text for the blog")
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]
    
    def get_context(self, request, *args, **kwargs):
        """获取博客文章列表上下文（分页 + 归档筛选）"""
        context = super().get_context(request, *args, **kwargs)
        
        # 获取筛选参数
        filter_year = request.GET.get('year')
        filter_month = request.GET.get('month')
        filter_day = request.GET.get('day')
        
        # 获取所有文章
        all_posts = list(self.get_children().specific().live())
        
        # 按日期倒序排序（先按date排序，date为空时用first_published_at）
        def sort_key(post):
            if hasattr(post, 'date') and post.date:
                return post.date
            elif hasattr(post, 'first_published_at') and post.first_published_at:
                return post.first_published_at
            return post.pk  # 如果都没有，使用pk作为后备
        
        all_posts.sort(key=sort_key, reverse=True)
        
        # 获取所有文章的年份，用于确定默认显示的年份
        all_years = set()
        for post in all_posts:
            post_date = self._get_post_date(post)
            if post_date:
                all_years.add(post_date.year)
        
        # 默认显示最近一年的文章（如果没有筛选）
        default_year = max(all_years) if all_years else None
        if not filter_year and default_year:
            filter_year = str(default_year)
        
        # 如果有筛选参数，筛选文章
        if filter_year:
            year = int(filter_year)
            if filter_month:
                month = int(filter_month)
                if filter_day:
                    day = int(filter_day)
                    all_posts = [p for p in all_posts if self._get_post_date(p).year == year and self._get_post_date(p).month == month and self._get_post_date(p).day == day]
                else:
                    all_posts = [p for p in all_posts if self._get_post_date(p).year == year and self._get_post_date(p).month == month]
            else:
                all_posts = [p for p in all_posts if self._get_post_date(p).year == year]
        
        # 获取分页参数
        page = int(request.GET.get('page', 1))
        per_page = 10
        
        # 计算总数
        total_count = len(all_posts)
        total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1
        
        # 确保页码有效
        if page < 1:
            page = 1
        if page > total_pages and total_pages > 0:
            page = total_pages
        
        # 获取当前页的文章
        start = (page - 1) * per_page
        end = start + per_page
        posts = all_posts[start:end]
        
        # 生成页码范围（显示最多10页）
        page_range = []
        if total_pages <= 10:
            page_range = list(range(1, total_pages + 1))
        else:
            if page <= 5:
                page_range = list(range(1, 11))
            elif page >= total_pages - 4:
                page_range = list(range(total_pages - 9, total_pages + 1))
            else:
                page_range = list(range(page - 4, page + 6))
        
        context['posts'] = posts
        context['current_page'] = page
        context['total_pages'] = total_pages
        context['total_count'] = total_count
        context['per_page'] = per_page
        context['page_range'] = page_range
        context['previous_page'] = page - 1 if page > 1 else 1
        context['next_page'] = page + 1 if page < total_pages else total_pages
        context['filter_year'] = int(filter_year) if filter_year else None
        context['filter_month'] = int(filter_month) if filter_month else None
        context['filter_day'] = int(filter_day) if filter_day else None
        
        # 生成文章归档（年份 -> 月份 -> 文章列表）
        # 重新获取所有文章用于归档（不包含筛选）
        all_posts_full = list(self.get_children().specific().live())
        all_posts_full.sort(key=sort_key, reverse=True)
        
        from collections import defaultdict
        archive = defaultdict(list)
        
        for post in all_posts_full:
            post_date = self._get_post_date(post)
            if post_date:
                key = (post_date.year, post_date.month)
                archive[key].append(post)
        
        # 转换为有序字典 {year: {month: [posts]}}
        archive_sorted = {}
        for year_month, posts in archive.items():
            year, month = year_month
            if year not in archive_sorted:
                archive_sorted[year] = {}
            archive_sorted[year][month] = posts
        
        # 按年份和月份排序
        for year in archive_sorted:
            archive_sorted[year] = dict(sorted(archive_sorted[year].items(), reverse=True))
        
        context['archive'] = dict(sorted(archive_sorted.items(), reverse=True))
        
        # 简化归档列表：当前年份月份 [(month, count), ...]
        current_year = int(filter_year) if filter_year else (max(archive_sorted.keys()) if archive_sorted else None)
        
        # 生成当前年份的月份列表
        months_with_posts = []
        if current_year and current_year in archive_sorted:
            for month in sorted(archive_sorted[current_year].keys(), reverse=True):
                count = len(archive_sorted[current_year][month])
                months_with_posts.append((month, count))
        
        # 判断是否有上一年/下一年
        all_years = sorted(archive_sorted.keys(), reverse=True)
        has_prev_year = current_year and current_year < max(all_years) if all_years else False
        has_next_year = current_year and current_year > min(all_years) if all_years else False
        
        context['current_year'] = current_year
        context['months_with_posts'] = months_with_posts
        context['has_prev_year'] = has_prev_year
        context['has_next_year'] = has_next_year
        
        # 保留旧的archive_list以兼容其他可能使用的地方
        archive_list = []
        for year in all_years:
            months_list = []
            for month in sorted(archive_sorted[year].keys(), reverse=True):
                count = len(archive_sorted[year][month])
                months_list.append((month, count))
            archive_list.append((year, months_list))
        context['archive_list'] = archive_list
        
        return context
    
    def _get_post_date(self, post):
        """获取文章发布日期"""
        if hasattr(post, 'date') and post.date:
            return post.date
        elif hasattr(post, 'first_published_at') and post.first_published_at:
            return post.first_published_at.date()
        return None


class BlogPage(Page):
    """博客文章页面"""
    date = models.DateField("发布日期", null=True, blank=True)
    intro = models.CharField("摘要", max_length=250, blank=True)
    body = RichTextField("文章内容", blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        FieldPanel('body'),
    ]
    
    template = 'home/blog_page.html'
    
    def get_context(self, request, *args, **kwargs):
        """获取博客文章上下文"""
        context = super().get_context(request, *args, **kwargs)
        context['comments'] = self.get_comments()
        return context
    
    def get_comments(self):
        """获取文章的评论"""
        return self.comments.filter(is_approved=True).order_by('-created_at')
    
    def get_comment_count(self):
        """获取评论数量"""
        return self.comments.filter(is_approved=True).count()


class Comment(models.Model):
    """文章评论模型"""
    blog_page = models.ForeignKey(
        BlogPage, 
        on_delete=models.CASCADE, 
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comments'
    )
    author_name = models.CharField("用户名", max_length=100)
    author_email = models.EmailField("邮箱")
    content = models.TextField("评论内容")
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)
    is_approved = models.BooleanField("是否通过审核", default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "评论"
        verbose_name_plural = "评论"
    
    def __str__(self):
        return f"{self.author_name} - {self.blog_page.title[:20]}"


class CustomPage(Page):
    """自定义页面 - 用于导入WordPress的其他栏目页面"""
    intro = models.CharField("摘要", max_length=250, blank=True)
    body = RichTextField("页面内容", blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('body'),
    ]
    
    template = 'home/custom_page.html'
    
    class Meta:
        verbose_name = "自定义页面"
        verbose_name_plural = "自定义页面"
