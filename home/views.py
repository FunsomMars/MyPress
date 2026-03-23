from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from .models import BlogPage, BlogIndexPage, Comment, GroupApplication, CustomPage


def index(request):
    """首页"""
    from home.models import BlogIndexPage
    
    # 获取博客索引页的文章，按日期排序（最新优先）
    blog_index = BlogIndexPage.objects.first()
    if blog_index:
        blog_posts = list(blog_index.get_children().specific().live())
        # 按日期倒序排序
        blog_posts.sort(key=lambda x: x.date, reverse=True)
        # 首页最多显示6篇文章
        display_posts = blog_posts[:6]
        # 是否显示"查看更多"按钮
        show_more = len(blog_posts) > 6
    else:
        display_posts = []
        show_more = False
    
    # 获取博客专栏链接
    blog_url = blog_index.url if blog_index else '/blog/'
    
    return render(request, 'home/index.html', {
        'blog_posts': display_posts,
        'show_more': show_more,
        'blog_url': blog_url
    })


def user_login(request):
    """用户登录"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # 检查是否验证了邮箱
            from home.models import EmailVerification
            if EmailVerification.objects.filter(user=user).exists():
                messages.error(request, '请先完成邮箱验证后再登录。验证邮件已发送到您的邮箱。')
                return render(request, 'home/login.html')
            
            # 设置会话超时：勾选"记住我"14天，否则8小时
            remember_me = request.POST.get('remember_me')
            if remember_me:
                request.session.set_expiry(14 * 24 * 3600)  # 14天
            else:
                request.session.set_expiry(8 * 3600)  # 8小时

            login(request, user)
            messages.success(request, f'欢迎回来, {user.username}!')
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, '用户名或密码错误')
    
    return render(request, 'home/login.html')


def user_register(request):
    """用户注册"""
    from django.contrib.auth import get_user_model
    from home.models import EmailVerification
    from django.core.mail import send_mail
    from django.conf import settings
    
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
        
        User = get_user_model()
        
        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            messages.error(request, f'用户名 "{username}" 已存在，请直接登录或使用其他用户名')
            return render(request, 'home/register.html')
        
        # 检查邮箱是否已存在
        if User.objects.filter(email=email).exists():
            messages.error(request, f'邮箱 "{email}" 已被注册，请直接登录或使用其他邮箱')
            return render(request, 'home/register.html')
        
        # 创建用户（未激活）
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            is_active=True  # 保持活跃，但需要邮箱验证
        )
        
        # 创建验证记录
        verification = EmailVerification.create_for_user(user)
        
        # 发送验证邮件
        site_url = 'www.mspace.top'
        verification_url = f"https://{site_url}/accounts/verify/{verification.verification_code}/"
        
        try:
            send_mail(
                subject='【MyPress】邮箱验证',
                message=f'您好 {username}，\n\n感谢注册 MyPress！\n\n请点击以下链接完成邮箱验证：\n{verification_url}\n\n链接有效期为24小时。\n\n如果这不是您的操作，请忽略此邮件。',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(request, '注册成功！请前往邮箱查收验证邮件，完成验证后即可登录。')
        except Exception as e:
            messages.warning(request, f'注册成功，但验证邮件发送失败。请联系管理员。')
            # 开发环境直接显示验证链接
            if settings.DEBUG:
                messages.info(request, f'验证链接（开发模式）：{verification_url}')
        
        return render(request, 'home/register_success.html', {'email': email})
    
    return render(request, 'home/register.html')


def user_logout(request):
    """用户登出"""
    logout(request)
    messages.info(request, '您已成功登出')
    return redirect('/')


def verify_email(request, code):
    """邮箱验证"""
    from home.models import EmailVerification
    
    verification = EmailVerification.objects.filter(verification_code=code).first()
    
    if not verification:
        messages.error(request, '验证链接无效')
        return redirect('/')
    
    if not verification.is_valid():
        messages.error(request, '验证链接已过期，请重新注册')
        # 删除过期验证记录
        verification.delete()
        return redirect('/')
    
    # 验证成功
    user = verification.user
    verification.delete()
    
    # 自动登录
    login(request, user)
    
    # 渲染验证成功页面（带倒计时跳转）
    return render(request, 'home/verify_success.html', {'user': user})


def can_manage_articles(user):
    """检查用户是否有管理文章的权限"""
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name__in=['Editors', 'Moderators', 'Administrators']).exists())


@login_required
def create_article(request):
    """创建文章"""
    # 检查权限
    if not can_manage_articles(request.user):
        messages.error(request, '您没有创建文章的权限，请先加入编辑及以上用户组')
        return redirect('/accounts/profile/')
    if request.method == 'POST':
        title = request.POST.get('title')
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
    
    # 检查权限 - 编辑及以上用户组可以编辑
    if not can_manage_articles(request.user):
        messages.error(request, '您没有权限编辑这篇文章，需要编辑及以上用户组权限')
        return redirect(f'/blog/{slug}/')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        body = request.POST.get('body')
        date = request.POST.get('date')

        article.title = title
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
    
    # 检查权限 - 编辑及以上用户组可以删除
    if not can_manage_articles(request.user):
        messages.error(request, '您没有权限删除这篇文章，需要编辑及以上用户组权限')
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
    
    # 获取用户创建的文章（分页）
    from wagtail.models import Page
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    articles_query = Page.objects.filter(
        content_type__model='blogpage',
        owner=request.user
    ).specific()
    
    paginator = Paginator(articles_query, 10)  # 每页10篇
    page = request.GET.get('page', 1)
    try:
        user_articles = paginator.page(page)
    except PageNotAnInteger:
        user_articles = paginator.page(1)
    except EmptyPage:
        user_articles = paginator.page(paginator.num_pages)
    
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
    allowed_groups = ['Editors', 'Moderators', 'Administrators']
    if group_name not in allowed_groups:
        messages.error(request, '无效的用户组')
        return redirect('/accounts/profile/')
    
    # 超级管理员不能申请
    if request.user.is_superuser:
        messages.error(request, '超级管理员无需申请')
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
    
    # 管理员不能申请版主/编辑
    if group_name in ['Editors', 'Moderators'] and request.user.groups.filter(name='Administrators').exists():
        messages.error(request, '管理员不能申请低级权限')
        return redirect('/accounts/profile/')
    
    # 创建申请记录
    application = GroupApplication.objects.create(
        user=request.user,
        requested_group=group_name,
        status='pending'
    )
    
    group_display = '编辑' if group_name == 'Editors' else ('版主' if group_name == 'Moderators' else '管理员')
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
    
    # 先清除用户的所有组，确保只能有一个组
    application.user.groups.clear()
    
    # 将用户加入对应的用户组
    group = Group.objects.get(name=application.requested_group)
    application.user.groups.add(group)
    
    group_display = '编辑' if application.requested_group == 'Editors' else ('版主' if application.requested_group == 'Moderators' else '管理员')
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
    
    group_display = '编辑' if application.requested_group == 'Editors' else ('版主' if application.requested_group == 'Moderators' else '管理员')
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


# ==================== 用户管理（仅超级管理员） ====================

@login_required
def user_management(request):
    """用户管理页面（仅超级管理员）"""
    if not request.user.is_superuser:
        messages.error(request, '只有超级管理员可以访问用户管理')
        return redirect('/accounts/profile/')
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # 获取所有用户
    users = User.objects.all().order_by('-date_joined')
    
    # 获取所有用户组
    all_groups = Group.objects.all()
    
    return render(request, 'home/user_management.html', {
        'users': users,
        'all_groups': all_groups,
        'current_user': request.user
    })


@login_required
@require_http_methods(["POST"])
def edit_user(request, user_id):
    """编辑用户信息（仅超级管理员）"""
    if not request.user.is_superuser:
        messages.error(request, '只有超级管理员可以编辑用户')
        return redirect('/accounts/profile/')
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    target_user = get_object_or_404(User, id=user_id)
    
    # 不能修改超级管理员（除非是自己）
    if target_user.is_superuser and target_user != request.user:
        messages.error(request, '不能修改其他超级管理员的信息')
        return redirect('/accounts/profile/')
    
    # 获取提交的表单数据
    email = request.POST.get('email', '').strip()
    username = request.POST.get('username', '').strip()
    new_password = request.POST.get('new_password', '').strip()
    group_id = request.POST.get('group', '')
    
    # 验证用户名唯一性
    if username != target_user.username and User.objects.filter(username=username).exists():
        messages.error(request, f'用户名 "{username}" 已被使用')
        return redirect('/accounts/profile/users/')
    
    # 验证邮箱唯一性
    if email != target_user.email and User.objects.filter(email=email).exists():
        messages.error(request, f'邮箱 "{email}" 已被使用')
        return redirect('/accounts/profile/users/')
    
    # 更新用户信息
    target_user.email = email
    target_user.username = username
    
    if new_password:
        target_user.set_password(new_password)
        messages.info(request, '密码已更新')
    
    # 更新用户组
    target_user.groups.clear()
    if group_id:
        group = Group.objects.get(id=group_id)
        target_user.groups.add(group)
    
    target_user.save()
    messages.success(request, f'用户 "{username}" 信息已更新')
    
    return redirect('/accounts/profile/users/')


@login_required
@require_http_methods(["POST"])
def delete_user(request, user_id):
    """删除用户（仅超级管理员）"""
    if not request.user.is_superuser:
        messages.error(request, '只有超级管理员可以删除用户')
        return redirect('/accounts/profile/')
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    target_user = get_object_or_404(User, id=user_id)
    
    # 不能删除自己
    if target_user == request.user:
        messages.error(request, '不能删除自己的账户')
        return redirect('/accounts/profile/users/')
    
    # 不能删除其他超级管理员
    if target_user.is_superuser:
        messages.error(request, '不能删除超级管理员账户')
        return redirect('/accounts/profile/users/')
    
    username = target_user.username
    target_user.delete()
    messages.success(request, f'用户 "{username}" 已删除')

    return redirect('/accounts/profile/users/')


@login_required
def edit_custom_page(request, slug):
    """编辑专栏页面"""
    page_obj = get_object_or_404(CustomPage, slug=slug)

    # 检查权限 - 编辑及以上用户组可以编辑
    if not can_manage_articles(request.user):
        messages.error(request, '您没有权限编辑此页面，需要编辑及以上用户组权限')
        return redirect(f'/{slug}/')

    if request.method == 'POST':
        title = request.POST.get('title')
        body = request.POST.get('body', '')

        page_obj.title = title
        page_obj.body = body

        # 保存版本并发布
        revision = page_obj.save_revision()
        revision.publish()

        messages.success(request, '页面更新成功!')
        return redirect(f'/{slug}/')

    return render(request, 'home/edit_custom_page.html', {'page_obj': page_obj})
