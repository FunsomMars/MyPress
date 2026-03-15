from django.db import models

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel


class HomePage(Page):
    intro = RichTextField(blank=True, help_text="Introduction text for the homepage")
    
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
            context['blog_posts'] = blog_index.get_children().specific().live()
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
