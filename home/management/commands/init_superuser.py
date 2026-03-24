"""
自动创建超级管理员账号
从环境变量读取 SUPERUSER_USERNAME / SUPERUSER_PASSWORD / SUPERUSER_EMAIL
如果账号已存在则跳过，不会覆盖现有账号
"""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = '从环境变量自动创建超级管理员（已存在则跳过）'

    def handle(self, *args, **options):
        username = getattr(settings, 'MYPRESS_SUPERUSER_USERNAME', '')
        password = getattr(settings, 'MYPRESS_SUPERUSER_PASSWORD', '')
        email = getattr(settings, 'MYPRESS_SUPERUSER_EMAIL', '')

        if not username or not password:
            self.stdout.write('未配置 SUPERUSER_USERNAME 或 SUPERUSER_PASSWORD，跳过超级管理员创建')
            return

        User = get_user_model()

        if User.objects.filter(username=username).exists():
            self.stdout.write(f'超级管理员 "{username}" 已存在，跳过')
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(f'✓ 已创建超级管理员: {username}'))
