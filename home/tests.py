"""
MyPress 博客系统单元测试

运行方式: python manage.py test home.tests --settings=my_press.settings.dev
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from home.models import BlogPage, BlogIndexPage, GroupApplication, Comment
from django.contrib.auth.models import Group


class UserAuthTest(TestCase):
    """用户认证测试"""
    
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_login(self):
        """测试用户登录"""
        response = self.client.login(username='testuser', password='testpass123')
        self.assertTrue(response)
    
    def test_user_login_wrong_password(self):
        """测试用户登录-错误密码"""
        response = self.client.login(username='testuser', password='wrongpass')
        self.assertFalse(response)
    
    def test_user_register(self):
        """测试用户注册"""
        User = get_user_model()
        response = self.client.post(reverse('user_register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
        })
        # 注册成功会重定向
        self.assertIn(response.status_code, [200, 302])


class UserGroupApplicationTest(TestCase):
    """用户组申请测试"""
    
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建 Editors 和 Moderators 组
        self.editors_group, _ = Group.objects.get_or_create(name='Editors')
        self.moderators_group, _ = Group.objects.get_or_create(name='Moderators')
    
    def test_user_can_apply_for_editors(self):
        """测试用户可以申请 Editors 组"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('join_group', args=['Editors']))
        
        # 检查是否创建了申请
        application = GroupApplication.objects.filter(
            user=self.user,
            requested_group='Editors',
            status='pending'
        ).first()
        
        self.assertIsNotNone(application)
    
    def test_user_cannot_apply_twice(self):
        """测试用户不能重复申请"""
        self.client.login(username='testuser', password='testpass123')
        
        # 第一次申请
        self.client.get(reverse('join_group', args=['Editors']))
        # 第二次申请
        self.client.get(reverse('join_group', args=['Editors']))
        
        # 检查申请数量
        count = GroupApplication.objects.filter(
            user=self.user,
            requested_group='Editors',
            status='pending'
        ).count()
        
        self.assertEqual(count, 1)
    
    def test_approve_application(self):
        """测试批准申请"""
        # 创建申请
        application = GroupApplication.objects.create(
            user=self.user,
            requested_group='Editors',
            status='pending'
        )
        
        # 创建超级管理员
        User = get_user_model()
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.client.login(username='admin', password='adminpass123')
        
        # 批准申请
        response = self.client.post(
            reverse('approve_application', args=[application.id]),
            {'action': 'approve', 'note': 'Approved'}
        )
        
        # 刷新数据库
        application.refresh_from_db()
        
        self.assertEqual(application.status, 'approved')
        self.assertTrue(self.user.groups.filter(name='Editors').exists())
    
    def test_reject_application(self):
        """测试拒绝申请"""
        # 创建申请
        application = GroupApplication.objects.create(
            user=self.user,
            requested_group='Editors',
            status='pending'
        )
        
        # 创建超级管理员
        User = get_user_model()
        admin = User.objects.create_superuser(
            username='admin2',
            email='admin2@example.com',
            password='adminpass123'
        )
        
        self.client.login(username='admin2', password='adminpass123')
        
        # 拒绝申请
        response = self.client.post(
            reverse('approve_application', args=[application.id]),
            {'action': 'reject', 'note': 'Not qualified'}
        )
        
        # 刷新数据库
        application.refresh_from_db()
        
        self.assertEqual(application.status, 'rejected')
        self.assertFalse(self.user.groups.filter(name='Editors').exists())
    
    def test_moderators_can_approve(self):
        """测试 Moderators 可以审批申请"""
        # 创建申请
        application = GroupApplication.objects.create(
            user=self.user,
            requested_group='Editors',
            status='pending'
        )
        
        # 创建 Moderators 用户
        User = get_user_model()
        mod = User.objects.create_user(
            username='moderator',
            email='mod@example.com',
            password='modpass123'
        )
        mod.groups.add(self.moderators_group)
        
        self.client.login(username='moderator', password='modpass123')
        
        # 批准申请
        response = self.client.post(
            reverse('approve_application', args=[application.id]),
            {'action': 'approve', 'note': 'Approved by mod'}
        )
        
        application.refresh_from_db()
        self.assertEqual(application.status, 'approved')


class BlogPageTest(TestCase):
    """博客页面访问测试"""
    
    def setUp(self):
        self.client = Client()
    
    def test_blog_index_accessible(self):
        """测试博客首页可访问"""
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
    
    def test_blog_index_calendar(self):
        """测试博客日历筛选-年份"""
        response = self.client.get('/blog/?year=2020')
        self.assertEqual(response.status_code, 200)
    
    def test_blog_index_calendar_year_month(self):
        """测试博客日历筛选-年月"""
        response = self.client.get('/blog/?year=2020&month=1')
        self.assertEqual(response.status_code, 200)


class HomepageTest(TestCase):
    """首页访问测试"""
    
    def setUp(self):
        self.client = Client()
    
    def test_homepage_accessible(self):
        """测试首页可访问"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class ProfileTest(TestCase):
    """个人中心测试"""
    
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_profile_requires_login(self):
        """测试个人中心需要登录"""
        response = self.client.get('/accounts/profile/')
        # 未登录会重定向到登录页
        self.assertEqual(response.status_code, 302)
    
    def test_profile_accessible_when_logged_in(self):
        """测试登录后可访问个人中心"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/accounts/profile/')
        self.assertEqual(response.status_code, 200)


class CommentTest(TestCase):
    """评论功能测试"""
    
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(
            username='commenter',
            email='commenter@example.com',
            password='commentpass123'
        )
    
    def test_add_comment_requires_login(self):
        """测试添加评论需要登录"""
        response = self.client.post('/blog/add-comment/test-slug/', {
            'content': 'Test comment'
        })
        # 未登录会返回错误或重定向
        self.assertIn(response.status_code, [302, 403, 500])
