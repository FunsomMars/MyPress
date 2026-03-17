from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from .models import BlogPage, BlogIndexPage, Comment, GroupApplication


def index(request):
    """首页"""
    from home.models import BlogIndexPage
    
    # 获取博客索引页的文章
    blog_index = BlogIndexPage.objects.first()
    if blog_index:
        blog_posts = blog_index.get_children().specific().live()
    else:
        blog_posts = []
    
    return render(request, 'home/index.html', {'blog_posts': blog_posts})


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


def can_manage_articles(user):
    """检查用户是否有管理文章的权限"""
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name__in=['Editors', 'Moderators']).exists())


@login_required
def create_article(request):
    """创建文章"""
    # 检查权限
    if not can_manage_articles(request.user):
        messages.error(request, '您没有创建文章的权限，请先加入 Editors 或 Moderators 用户组')
        return redirect('/accounts/profile/')
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
    
    # 获取用户所属组
    user_groups = request.user.groups.all()
    
    # 获取用户的申请
    my_applications = GroupApplication.objects.filter(user=request.user).order_by('-created_at')
    
    # 获取待审批的申请（仅超级管理员可见）
    all_applications = []
    if request.user.is_superuser:
        # 超级管理员可以看到所有申请
        all_applications = GroupApplication.objects.all().order_by('-created_at')[:30]
    
    # 检查用户是否有管理文章权限
    can_manage = can_manage_articles(request.user)
    
    return render(request, 'home/profile.html', {
        'user_articles': user_articles,
        'user_groups': user_groups,
        'my_applications': my_applications,
        'all_applications': all_applications,
        'can_manage': can_manage
    })


@login_required
def join_group(request, group_name):
    """用户申请加入用户组"""
    # 只有特定组可以申请加入
    allowed_groups = ['Editors', 'Moderators']
    if group_name not in allowed_groups:
        messages.error(request, '无效的用户组')
        return redirect('/accounts/profile/')
    
    # 超级管理员不能申请
    if request.user.is_superuser:
        messages.error(request, '超级管理员无需申请')
        return redirect('/accounts/profile/')
    
    # 检查是否已经是该组成员
    if request.user.groups.filter(name=group_name).exists():
        group_display = '编辑' if group_name == 'Editors' else '版主'
        messages.info(request, f'您已经是{group_display}组的成员')
        return redirect('/accounts/profile/')
    
    # 检查是否已有待审批的申请
    existing_application = GroupApplication.objects.filter(
        user=request.user,
        requested_group=group_name,
        status='pending'
    ).first()
    
    if existing_application:
        messages.info(request, '您已有待审批的申请，请耐心等待')
        return redirect('/accounts/profile/')
    
    # 检查权限：不能向下申请
    # 版主不能申请编辑
    if group_name == 'Editors' and request.user.groups.filter(name='Moderators').exists():
        messages.error(request, '版主不能申请编辑权限')
        return redirect('/accounts/profile/')
    
    # 创建申请记录
    application = GroupApplication.objects.create(
        user=request.user,
        requested_group=group_name,
        status='pending'
    )
    
    group_display = '编辑' if group_name == 'Editors' else '版主'
    messages.success(request, f'您的{group_display}权限申请已提交，请等待审批！')
    
    return redirect('/accounts/profile/')


@login_required
@require_http_methods(["POST"])
def approve_application(request, application_id):
    """审批用户组申请"""
    # 检查权限：只有超级管理员可以审批
    if not request.user.is_superuser:
        messages.error(request, '只有超级管理员可以审批申请')
        return redirect('/accounts/profile/')
    
    application = get_object_or_404(GroupApplication, id=application_id, status='pending')
    
    # 审批通过
    application.status = 'approved'
    application.reviewed_by = request.user
    application.save()
    
    # 将用户加入对应的用户组
    group = Group.objects.get(name=application.requested_group)
    application.user.groups.add(group)
    
    group_display = '编辑' if application.requested_group == 'Editors' else '版主'
    messages.success(request, f'已批准 {application.user.username} 的{group_display}权限申请')
    
    return redirect('/accounts/profile/')


@login_required
@require_http_methods(["POST"])
def reject_application(request, application_id):
    """拒绝用户组申请"""
    # 检查权限：只有超级管理员可以审批
    if not request.user.is_superuser:
        messages.error(request, '只有超级管理员可以审批申请')
        return redirect('/accounts/profile/')
    
    application = get_object_or_404(GroupApplication, id=application_id, status='pending')
    
    # 拒绝申请
    application.status = 'rejected'
    application.reviewed_by = request.user
    application.save()
    
    group_display = '编辑' if application.requested_group == 'Editors' else '版主'
    messages.success(request, f'已拒绝 {application.user.username} 的{group_display}权限申请')
    
    return redirect('/accounts/profile/')


@login_required
@require_http_methods(["POST"])
def cancel_application(request, application_id):
    """用户取消申请"""
    application = get_object_or_404(GroupApplication, id=application_id, user=request.user, status='pending')
    
    application.delete()
    
    messages.success(request, '申请已取消')
    
    return redirect('/accounts/profile/')
