"""
URL configuration for projectname project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from members.views import order_ticket
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

# 定义主页视图
# def homepage(request):
#     return HttpResponse("Welcome to the homepage!")

# 主 URL 模式
urlpatterns = [
    path('', include('members.urls')),  # 包含 members 应用的 URL
    path('subscriptions/', include('subscriptions.urls', namespace='subscriptions')),  # 包含 subscriptions 应用的 URL，并指定命名空间
    # path('', homepage, name='home'),  # 给首页添加 name='home'
    path('admin/', admin.site.urls),  # 定义 admin URL
    path('set_language/', include('django.conf.urls.i18n')),  # 添加语言切换路径
]

# 处理媒体文件的静态路径，仅在开发环境中处理
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 处理媒体文件
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)