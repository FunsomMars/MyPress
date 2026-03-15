from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel


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
            # 使用list()强制评估查询集，确保模板能正确渲染
            posts = list(blog_index.get_children().specific().live()[:6])
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
        """获取博客文章列表上下文"""
        context = super().get_context(request, *args, **kwargs)
        # 获取所有已发布的博客文章页面
        context['posts'] = self.get_children().specific().live()
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
