from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail

from .models import BlogPage, BlogIndexPage, Comment, EmailVerification


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
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # 检查用户是否存在（大小写敏感）
        user_exists = User.objects.filter(username__exact=username).exists()
        
        if not user_exists:
            # 检查是否是因为大小写问题
            similar_users = User.objects.filter(username__icontains=username)
            if similar_users.exists():
                messages.error(request, f'用户 "{username}" 不存在，是否输入了错误的大小写？请重试。')
            else:
                messages.error(request, '用户名或密码错误')
            return render(request, 'home/login.html')
        
        # 检查用户是否存在且已激活
        try:
            user = User.objects.get(username=username)
            if not user.is_active:
                messages.error(request, '您的账户尚未通过邮箱验证，请先查收验证邮件完成激活。')
                return render(request, 'home/login.html')
        except User.DoesNotExist:
            pass
        
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
    """用户注册 - 需要邮箱验证"""
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
        
        # 大小写敏感的用户名检查
        if User.objects.filter(username__exact=username).exists():
            return render(request, 'home/register.html', {
                'error_message': f'用户名 "{username}" 已被注册',
                'show_login_link': True
            })
        
        # 大小写敏感的邮箱检查
        if User.objects.filter(email__exact=email).exists():
            return render(request, 'home/register.html', {
                'error_message': f'邮箱 "{email}" 已被注册',
                'show_login_link': True
            })
        
        # 创建用户，但设置为未激活状态
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            is_active=False  # 需要邮箱验证后才能激活
        )
        
        # 创建邮箱验证记录
        verification = EmailVerification.create_for_user(user)
        
        # 发送验证邮件
        verification_url = request.build_absolute_uri(f'/accounts/verify/{verification.verification_code}/')
        
        try:
            send_mail(
                subject='【MyPress】邮箱验证 - 激活您的账户',
                message=f'''您好 {username}，

感谢您注册 MyPress！

请点击下面的链接完成邮箱验证：
{verification_url}

此链接有效期为24小时。

如果以上链接无法点击，请复制以下链接到浏览器打开：
{verification_url}

---
MyPress 团队
''',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            # 注册成功，跳转到成功提示页面
            return render(request, 'home/register_success.html', {
                'email': email,
                'next_url': request.GET.get('next', '/')
            })
        except Exception as e:
            # 邮件发送失败时，仍然创建未激活用户，等待手动激活
            # 可以记录日志或在管理后台处理
            print(f"邮件发送失败: {e}")
            # 邮件发送失败也跳转到成功页面
            return render(request, 'home/register_success.html', {
                'email': email,
                'next_url': request.GET.get('next', '/'),
                'email_failed': True
            })
    
    return render(request, 'home/register.html')


def verify_email(request, verification_code):
    """邮箱验证"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    verification = get_object_or_404(EmailVerification, verification_code=verification_code)
    
    # 检查是否过期
    if not verification.is_valid():
        messages.error(request, '验证链接已过期，请重新注册')
        return redirect('/accounts/register/')
    
    # 激活用户
    user = verification.user
    user.is_active = True
    user.save()
    
    # 删除验证记录
    verification.delete()
    
    # 自动登录
    login(request, user)
    messages.success(request, f'邮箱验证成功！欢迎 {user.username}！')
    return redirect('/')


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
    
    # 检查用户是否可以管理文章（超级管理员或Editors/Moderators组）
    can_manage = request.user.is_superuser or request.user.groups.filter(name__in=['Editors', 'Moderators']).exists()
    
    # 获取用户创建的文章
    from wagtail.models import Page
    user_articles = Page.objects.filter(
        content_type__model='blogpage',
        owner=request.user
    ).specific()
    
    # 获取用户所属组
    user_groups = request.user.groups.all()
    
    return render(request, 'home/profile.html', {
        'user_articles': user_articles,
        'user_groups': user_groups,
        'can_manage': can_manage
    })


@login_required
def join_group(request, group_name):
    """用户申请加入用户组"""
    from django.contrib.auth.models import Group
    
    # 只有特定组可以申请加入
    allowed_groups = ['Editors', 'Moderators']
    if group_name not in allowed_groups:
        messages.error(request, '无效的用户组')
        return redirect('/accounts/profile/')
    
    try:
        group = Group.objects.get(name=group_name)
        if request.user.groups.filter(name=group_name).exists():
            messages.info(request, f'您已经是 {group_name} 组的成员')
        else:
            request.user.groups.add(group)
            messages.success(request, f'已成功加入 {group_name} 组！')
    except Group.DoesNotExist:
        messages.error(request, '用户组不存在')
    
    return redirect('/accounts/profile/')
