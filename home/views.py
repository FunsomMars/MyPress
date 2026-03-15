from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from .models import BlogPage, BlogIndexPage, Comment


def index(request):
    """首页"""
    return render(request, 'home/index.html')


def user_login(request):
    """用户登录"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'欢迎回来, {user.username}!')
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, '用户名或密码错误')
    
    return render(request, 'home/login.html')


def user_register(request):
    """用户注册"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # 验证
        if password1 != password2:
            messages.error(request, '两次密码不一致')
            return render(request, 'home/register.html')
        
        if len(password1) < 6:
            messages.error(request, '密码长度至少6位')
            return render(request, 'home/register.html')
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
            return render(request, 'home/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, '邮箱已被注册')
            return render(request, 'home/register.html')
        
        # 创建用户
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )
        
        # 自动登录
        login(request, user)
        messages.success(request, '注册成功!')
        return redirect('/')
    
    return render(request, 'home/register.html')


def user_logout(request):
    """用户登出"""
    logout(request)
    messages.info(request, '您已成功登出')
    return redirect('/')


@login_required
def create_article(request):
    """创建文章"""
    if request.method == 'POST':
        title = request.POST.get('title')
        intro = request.POST.get('intro')
        body = request.POST.get('body')
        date = request.POST.get('date')
        
        # 获取博客索引页
        blog_index = BlogIndexPage.objects.first()
        if not blog_index:
            messages.error(request, '博客索引页不存在')
            return redirect('/')
        
        # 生成slug
        from django.utils.text import slugify
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        while BlogPage.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # 创建文章
        article = BlogPage(
            title=title,
            slug=slug,
            intro=intro[:250] if intro else title[:100],
            body=body,
        )
        
        if date:
            from datetime import datetime
            try:
                article.date = datetime.strptime(date, '%Y-%m-%d').date()
            except:
                article.date = timezone.now().date()
        else:
            article.date = timezone.now().date()
        
        blog_index.add_child(instance=article)
        
        # 保存版本并发布
        revision = article.save_revision()
        revision.publish()
        
        messages.success(request, '文章创建成功!')
        return redirect(f'/blog/{slug}/')
    
    return render(request, 'home/create_article.html')


@login_required
def edit_article(request, slug):
    """编辑文章"""
    article = get_object_or_404(BlogPage, slug=slug)
    
    # 检查权限 - 作者或超级用户可以编辑
    if request.user != article.owner and not request.user.is_superuser:
        messages.error(request, '您没有权限编辑这篇文章')
        return redirect(f'/blog/{slug}/')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        intro = request.POST.get('intro')
        body = request.POST.get('body')
        date = request.POST.get('date')
        
        article.title = title
        article.intro = intro[:250] if intro else title[:100]
        article.body = body
        
        if date:
            from datetime import datetime
            try:
                article.date = datetime.strptime(date, '%Y-%m-%d').date()
            except:
                pass
        
        # 保存版本并发布
        revision = article.save_revision()
        revision.publish()
        
        messages.success(request, '文章更新成功!')
        return redirect(f'/blog/{slug}/')
    
    return render(request, 'home/edit_article.html', {'article': article})


@login_required
def delete_article(request, slug):
    """删除文章"""
    article = get_object_or_404(BlogPage, slug=slug)
    
    # 检查权限 - 作者或超级用户可以删除
    if request.user != article.owner and not request.user.is_superuser:
        messages.error(request, '您没有权限删除这篇文章')
        return redirect(f'/blog/{slug}/')
    
    if request.method == 'POST':
        article.delete()
        messages.success(request, '文章已删除')
        return redirect('/blog/')
    
    return render(request, 'home/delete_article.html', {'article': article})


@require_http_methods(["POST"])
def add_comment(request, slug):
    """添加评论"""
    article = get_object_or_404(BlogPage, slug=slug)
    
    content = request.POST.get('content', '').strip()
    
    if not content:
        return JsonResponse({'success': False, 'error': '评论内容不能为空'})
    
    if request.user.is_authenticated:
        author = request.user
        author_name = author.username
        author_email = author.email
    else:
        author = None
        author_name = request.POST.get('author_name', '').strip()
        author_email = request.POST.get('author_email', '').strip()
        
        if not author_name:
            return JsonResponse({'success': False, 'error': '请填写用户名'})
        if not author_email:
            return JsonResponse({'success': False, 'error': '请填写邮箱'})
    
    # 创建评论
    comment = Comment.objects.create(
        blog_page=article,
        author=author,
        author_name=author_name,
        author_email=author_email,
        content=content,
        is_approved=True  # 直接通过审核
    )
    
    return JsonResponse({
        'success': True,
        'comment': {
            'author_name': comment.author_name,
            'content': comment.content,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
        }
    })


@login_required
def manage_comments(request):
    """管理评论（仅管理员）"""
    if not request.user.is_superuser:
        messages.error(request, '只有管理员可以管理评论')
        return redirect('/')
    
    comments = Comment.objects.all().order_by('-created_at')
    
    return render(request, 'home/manage_comments.html', {'comments': comments})


@login_required
def delete_comment(request, comment_id):
    """删除评论（仅管理员）"""
    if not request.user.is_superuser:
        messages.error(request, '只有管理员可以删除评论')
        return redirect('/')
    
    comment = get_object_or_404(Comment, id=comment_id)
    comment.delete()
    messages.success(request, '评论已删除')
    
    return redirect('/manage/comments/')


def user_profile(request):
    """用户个人中心"""
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    
    # 获取用户创建的文章
    from wagtail.models import Page
    user_articles = Page.objects.filter(
        content_type__model='blogpage',
        owner=request.user
    ).specific()
    
    return render(request, 'home/profile.html', {
        'user_articles': user_articles
    })
