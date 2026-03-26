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
    """Home page"""
    from home.models import BlogIndexPage
    
    # Get posts from blog index, sorted by date (newest first)
    blog_index = BlogIndexPage.objects.first()
    if blog_index:
        blog_posts = list(blog_index.get_children().specific().live())
        # Sort by date descending
        blog_posts.sort(key=lambda x: x.date, reverse=True)
        # Show max 6 posts on homepage
        display_posts = blog_posts[:6]
        # Show "view more" button flag
        show_more = len(blog_posts) > 6
    else:
        display_posts = []
        show_more = False
    
    # Get blog section URL
    blog_url = blog_index.url if blog_index else '/blog/'
    
    return render(request, 'home/index.html', {
        'blog_posts': display_posts,
        'show_more': show_more,
        'blog_url': blog_url
    })


def user_login(request):
    """User login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if email is verified
            from home.models import EmailVerification
            if EmailVerification.objects.filter(user=user).exists():
                messages.error(request, 'Please verify your email before logging in. Verification email has been sent.')
                return render(request, 'home/login.html')
            
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'home/login.html')


def user_register(request):
    """User registration"""
    from django.contrib.auth import get_user_model
    from home.models import EmailVerification
    from django.core.mail import send_mail
    from django.conf import settings
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validate passwords match
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'home/register.html')
        
        if len(password1) < 6:
            messages.error(request, 'Password must be at least 6 characters')
            return render(request, 'home/register.html')
        
        User = get_user_model()
        
        # Check if username exists
        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" already exists. Please login or use a different username.')
            return render(request, 'home/register.html')
        
        # Check if email exists
        if User.objects.filter(email=email).exists():
            messages.error(request, f'Email "{email}" is already registered. Please login or use a different email.')
            return render(request, 'home/register.html')
        
        # Create user (inactive until email verified)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            is_active=True  # Keep active, but requires email verification
        )
        
        # Create verification record
        verification = EmailVerification.create_for_user(user)
        
        # Send verification email
        site_url = 'www.mspace.top'
        verification_url = f"https://{site_url}/accounts/verify/{verification.verification_code}/"
        
        try:
            send_mail(
                subject='[MyPress] Email Verification',
                message=f'Hi {username},\n\nThank you for registering with MyPress!\n\nPlease click the link below to verify your email:\n{verification_url}\n\nThis link expires in 24 hours.\n\nIf this was not you, please ignore this email.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(request, 'Registration successful! Please check your email for the verification link.')
        except Exception as e:
            messages.warning(request, f'Registration successful, but failed to send verification email. Please contact admin.')
            # Show verification link in dev mode
            if settings.DEBUG:
                messages.info(request, f'Verification link (dev mode): {verification_url}')
        
        return render(request, 'home/register_success.html', {'email': email})
    
    return render(request, 'home/register.html')


def user_logout(request):
    """User logout"""
    logout(request)
    messages.info(request, 'You have been logged out successfully')
    return redirect('/')


def verify_email(request, code):
    """Email verification"""
    from home.models import EmailVerification
    
    verification = EmailVerification.objects.filter(verification_code=code).first()
    
    if not verification:
        messages.error(request, 'Invalid verification link')
        return redirect('/')
    
    if not verification.is_valid():
        messages.error(request, 'Verification link expired. Please register again.')
        # Delete expired verification record
        verification.delete()
        return redirect('/')
    
    # Verification successful
    user = verification.user
    verification.delete()
    
    # Auto login
    login(request, user)
    
    # Render verification success page (with countdown redirect)
    return render(request, 'home/verify_success.html', {'user': user})


def can_manage_articles(user):
    """Check if user has article management permission"""
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name__in=['Editors', 'Moderators', 'Administrators']).exists())


@login_required
def create_article(request):
    """Create article"""
    # Check permission
    if not can_manage_articles(request.user):
        messages.error(request, 'You do not have permission to create articles. Please join the Editor or higher user group first.')
        return redirect('/accounts/profile/')
    if request.method == 'POST':
        title = request.POST.get('title')
        intro = request.POST.get('intro')
        body = request.POST.get('body')
        date = request.POST.get('date')
        
        # Get blog index page
        blog_index = BlogIndexPage.objects.first()
        if not blog_index:
            messages.error(request, 'Blog index page does not exist')
            return redirect('/')
        
        # Generate slug
        from django.utils.text import slugify
        base_slug = slugify(title)
        slug = base_slug
        counter = 1
        while BlogPage.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Create article
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
        
        # Save revision and publish
        revision = article.save_revision()
        revision.publish()
        
        messages.success(request, 'Article created successfully!')
        return redirect(f'/blog/{slug}/')
    
    return render(request, 'home/create_article.html')


@login_required
def edit_article(request, slug):
    """Edit article"""
    article = get_object_or_404(BlogPage, slug=slug)
    
    # Check permission - author or superuser can edit
    if request.user != article.owner and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to edit this article')
        return redirect(f'/blog/{slug}/')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        intro = request.POST.get('intro')
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
        
        # Save revision and publish
        revision = article.save_revision()
        revision.publish()
        
        messages.success(request, 'Article updated successfully!')
        return redirect(f'/blog/{slug}/')
    
    return render(request, 'home/edit_article.html', {'article': article})


@login_required
def delete_article(request, slug):
    """Delete article"""
    article = get_object_or_404(BlogPage, slug=slug)
    
    # Check permission - author or superuser can delete
    if request.user != article.owner and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete this article')
        return redirect(f'/blog/{slug}/')
    
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Article deleted')
        return redirect('/blog/')
    
    return render(request, 'home/delete_article.html', {'article': article})


@require_http_methods(["POST"])
def add_comment(request, slug):
    """Add comment"""
    article = get_object_or_404(BlogPage, slug=slug)
    
    content = request.POST.get('content', '').strip()
    
    if not content:
        return JsonResponse({'success': False, 'error': 'Comment content cannot be empty'})
    
    if request.user.is_authenticated:
        author = request.user
        author_name = author.username
        author_email = author.email
    else:
        author = None
        author_name = request.POST.get('author_name', '').strip()
        author_email = request.POST.get('author_email', '').strip()
        
        if not author_name:
            return JsonResponse({'success': False, 'error': 'Please enter a username'})
        if not author_email:
            return JsonResponse({'success': False, 'error': 'Please enter an email'})
    
    # Create comment
    comment = Comment.objects.create(
        blog_page=article,
        author=author,
        author_name=author_name,
        author_email=author_email,
        content=content,
        is_approved=True  # Auto-approve
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
    """Manage comments (admin only)"""
    if not request.user.is_superuser:
        messages.error(request, 'Only administrators can manage comments')
        return redirect('/')
    
    comments = Comment.objects.all().order_by('-created_at')
    
    return render(request, 'home/manage_comments.html', {'comments': comments})


@login_required
def delete_comment(request, comment_id):
    """Delete comment (admin only)"""
    if not request.user.is_superuser:
        messages.error(request, 'Only administrators can delete comments')
        return redirect('/')
    
    comment = get_object_or_404(Comment, id=comment_id)
    comment.delete()
    messages.success(request, 'Comment deleted')
    
    return redirect('/manage/comments/')


def user_profile(request):
    """User profile page"""
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    
    # Get user's articles (paginated)
    from wagtail.models import Page
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    articles_query = Page.objects.filter(
        content_type__model='blogpage',
        owner=request.user
    ).specific()
    
    paginator = Paginator(articles_query, 10)  # 10 posts per page
    page = request.GET.get('page', 1)
    try:
        user_articles = paginator.page(page)
    except PageNotAnInteger:
        user_articles = paginator.page(1)
    except EmptyPage:
        user_articles = paginator.page(paginator.num_pages)
    
    # Get user's groups
    user_groups = request.user.groups.all()
    
    # Get user's applications
    my_applications = GroupApplication.objects.filter(user=request.user).order_by('-created_at')
    
    # Get pending applications (superadmin only)
    all_applications = []
    if request.user.is_superuser:
        # Super admin can see all applications
        all_applications = GroupApplication.objects.all().order_by('-created_at')[:30]
    
    # Check if user can manage articles
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
    """User applies to join user group"""
    # Only specific groups can be applied for
    allowed_groups = ['Editors', 'Moderators', 'Administrators']
    if group_name not in allowed_groups:
        messages.error(request, 'Invalid user group')
        return redirect('/accounts/profile/')
    
    # Super admin cannot apply
    if request.user.is_superuser:
        messages.error(request, 'Super admin does not need to apply')
        return redirect('/accounts/profile/')
    
    # Check if there's already a pending application
    existing_application = GroupApplication.objects.filter(
        user=request.user,
        requested_group=group_name,
        status='pending'
    ).first()
    
    if existing_application:
        messages.info(request, 'You already have a pending application. Please wait for approval.')
        return redirect('/accounts/profile/')
    
    # Permission check: cannot apply for lower privileges
    # Moderator cannot apply for Editor
    if group_name == 'Editors' and request.user.groups.filter(name='Moderators').exists():
        messages.error(request, 'Moderators cannot apply for Editor privileges')
        return redirect('/accounts/profile/')
    
    # Admin cannot apply for Moderator/Editor
    if group_name in ['Editors', 'Moderators'] and request.user.groups.filter(name='Administrators').exists():
        messages.error(request, 'Administrators cannot apply for lower privileges')
        return redirect('/accounts/profile/')
    
    # Create application record
    application = GroupApplication.objects.create(
        user=request.user,
        requested_group=group_name,
        status='pending'
    )
    
    group_display = 'Editor' if group_name == 'Editors' else ('Moderator' if group_name == 'Moderators' else 'Administrator')
    messages.success(request, f'Your {group_display} application has been submitted. Please wait for approval!')
    
    return redirect('/accounts/profile/')


@login_required
@require_http_methods(["POST"])
def approve_application(request, application_id):
    """Approve user group application"""
    # Check permission: only super admin can approve
    if not request.user.is_superuser:
        messages.error(request, 'Only super administrators can approve applications')
        return redirect('/accounts/profile/')
    
    application = get_object_or_404(GroupApplication, id=application_id, status='pending')
    
    # Approve application
    application.status = 'approved'
    application.reviewed_by = request.user
    application.save()
    
    # Clear all user's groups first to ensure only one group
    application.user.groups.clear()
    
    # Add user to the requested group
    group = Group.objects.get(name=application.requested_group)
    application.user.groups.add(group)
    
    group_display = 'Editor' if application.requested_group == 'Editors' else ('Moderator' if application.requested_group == 'Moderators' else 'Administrator')
    messages.success(request, f'Approved {application.user.username}\'s {group_display} application')
    
    return redirect('/accounts/profile/')


@login_required
@require_http_methods(["POST"])
def reject_application(request, application_id):
    """Reject user group application"""
    # Check permission: only super admin can reject
    if not request.user.is_superuser:
        messages.error(request, 'Only super administrators can reject applications')
        return redirect('/accounts/profile/')
    
    application = get_object_or_404(GroupApplication, id=application_id, status='pending')
    
    # Reject application
    application.status = 'rejected'
    application.reviewed_by = request.user
    application.save()
    
    group_display = 'Editor' if application.requested_group == 'Editors' else ('Moderator' if application.requested_group == 'Moderators' else 'Administrator')
    messages.success(request, f'Rejected {application.user.username}\'s {group_display} application')
    
    return redirect('/accounts/profile/')


@login_required
@require_http_methods(["POST"])
def cancel_application(request, application_id):
    """User cancels their application"""
    application = get_object_or_404(GroupApplication, id=application_id, user=request.user, status='pending')
    
    application.delete()
    
    messages.success(request, 'Application cancelled')
    
    return redirect('/accounts/profile/')


# ==================== User Management (Super Admin Only) ====================

@login_required
def user_management(request):
    """User management page (super admin only)"""
    if not request.user.is_superuser:
        messages.error(request, 'Only super administrators can access user management')
        return redirect('/accounts/profile/')
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Get all users
    users = User.objects.all().order_by('-date_joined')
    
    # Get all user groups
    all_groups = Group.objects.all()
    
    return render(request, 'home/user_management.html', {
        'users': users,
        'all_groups': all_groups,
        'current_user': request.user
    })


@login_required
@require_http_methods(["POST"])
def edit_user(request, user_id):
    """Edit user info (super admin only)"""
    if not request.user.is_superuser:
        messages.error(request, 'Only super administrators can edit users')
        return redirect('/accounts/profile/')
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    target_user = get_object_or_404(User, id=user_id)
    
    # Cannot edit other super admins (unless it's yourself)
    if target_user.is_superuser and target_user != request.user:
        messages.error(request, 'Cannot edit other super administrators')
        return redirect('/accounts/profile/')
    
    # Get submitted form data
    email = request.POST.get('email', '').strip()
    username = request.POST.get('username', '').strip()
    new_password = request.POST.get('new_password', '').strip()
    group_id = request.POST.get('group', '')
    
    # Validate username uniqueness
    if username != target_user.username and User.objects.filter(username=username).exists():
        messages.error(request, f'Username "{username}" is already taken')
        return redirect('/accounts/profile/users/')
    
    # Validate email uniqueness
    if email != target_user.email and User.objects.filter(email=email).exists():
        messages.error(request, f'Email "{email}" is already in use')
        return redirect('/accounts/profile/users/')
    
    # Update user info
    target_user.email = email
    target_user.username = username
    
    if new_password:
        target_user.set_password(new_password)
        messages.info(request, 'Password has been updated')
    
    # Update user groups
    target_user.groups.clear()
    if group_id:
        group = Group.objects.get(id=group_id)
        target_user.groups.add(group)
    
    target_user.save()
    messages.success(request, f'User "{username}" info updated')
    
    return redirect('/accounts/profile/users/')


@login_required
@require_http_methods(["POST"])
def delete_user(request, user_id):
    """Delete user (super admin only)"""
    if not request.user.is_superuser:
        messages.error(request, 'Only super administrators can delete users')
        return redirect('/accounts/profile/')
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    target_user = get_object_or_404(User, id=user_id)
    
    # Cannot delete yourself
    if target_user == request.user:
        messages.error(request, 'Cannot delete your own account')
        return redirect('/accounts/profile/users/')
    
    # Cannot delete other super admins
    if target_user.is_superuser:
        messages.error(request, 'Cannot delete super administrator accounts')
        return redirect('/accounts/profile/users/')
    
    username = target_user.username
    target_user.delete()
    messages.success(request, f'User "{username}" deleted')
    
    return redirect('/accounts/profile/users/')
