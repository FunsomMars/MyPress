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
            # 按发布日期倒序排列，获取最近的6篇文章
            posts = list(blog_index.get_children().specific().live().order_by('-date', '-first_published_at')[:6])
            context['blog_posts'] = posts
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
        """获取博客文章列表上下文（分页）"""
        context = super().get_context(request, *args, **kwargs)
        
        # 获取分页参数
        page = int(request.GET.get('page', 1))
        per_page = 10
        
        # 获取所有文章并按发布日期倒序（先按date排序，date为空时用first_published_at）
        all_posts = self.get_children().specific().live().order_by('-date', '-first_published_at')
        
        # 计算总数
        total_count = all_posts.count()
        total_pages = (total_count + per_page - 1) // per_page
        
        # 确保页码有效
        if page < 1:
            page = 1
        if page > total_pages and total_pages > 0:
            page = total_pages
        
        # 获取当前页的文章
        start = (page - 1) * per_page
        end = start + per_page
        posts = list(all_posts[start:end])
        
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
        
        return context


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
