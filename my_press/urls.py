from django.conf import settings
from django.urls import include, path
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views
import home.views as home_views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("search/", search_views.search, name="search"),
    
    # 用户认证 URLs
    path('accounts/login/', home_views.user_login, name='account_login'),
    path('accounts/register/', home_views.user_register, name='account_register'),
    path('accounts/logout/', home_views.user_logout, name='account_logout'),
    path('accounts/verify/<str:code>/', home_views.verify_email, name='verify_email'),
    path('accounts/profile/', home_views.user_profile, name='account_profile'),
    path('accounts/profile/users/', home_views.user_management, name='user_management'),
    path('accounts/profile/user/<int:user_id>/edit/', home_views.edit_user, name='edit_user'),
    path('accounts/profile/user/<int:user_id>/delete/', home_views.delete_user, name='delete_user'),
    path('accounts/join/<str:group_name>/', home_views.join_group, name='join_group'),
    path('accounts/application/<int:application_id>/approve/', home_views.approve_application, name='approve_application'),
    path('accounts/application/<int:application_id>/reject/', home_views.reject_application, name='reject_application'),
    path('accounts/application/<int:application_id>/cancel/', home_views.cancel_application, name='cancel_application'),
    
    # 前台文章管理 URLs
    path('article/create/', home_views.create_article, name='create_article'),
    path('article/<slug:slug>/edit/', home_views.edit_article, name='edit_article'),
    path('article/<slug:slug>/delete/', home_views.delete_article, name='delete_article'),
    
    # 评论 URLs
    path('article/<slug:slug>/comment/', home_views.add_comment, name='add_comment'),
    path('manage/comments/', home_views.manage_comments, name='manage_comments'),
    path('comment/<int:comment_id>/delete/', home_views.delete_comment, name='delete_comment'),
    
    # 首页
    path('', home_views.index, name='index'),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
