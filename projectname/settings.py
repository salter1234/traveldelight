import os
from pathlib import Path
import dj_database_url

# 奕誠
AUTH_USER_MODEL = 'members.Member'

# 設置專案的根目錄路徑
BASE_DIR = Path(__file__).resolve().parent.parent

# 快速開發設置，這些設置不適合用於生產環境
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', "django-insecure-18p*)w2q+_7p*o8@@8+14y1erm__6+@a#$@c8%h1@j93z#06@8")

# 注意：生產環境中不要啟用 debug 模式
DEBUG = False

ALLOWED_HOSTS = ['*']

# 應用程式定義
INSTALLED_APPS = [
    'social_django',
    'widget_tweaks',
    'jazzmin',  # Django Admin 美化介面
    'django_extensions',
    'members',  # 自定義會員系統
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'subscriptions',
]

MIDDLEWARE = [
    'social_django.middleware.SocialAuthExceptionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # WhiteNoise 处理静态文件
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # 确保这一行在前
    'django.middleware.locale.LocaleMiddleware',  # 語言中間件需放在這裏
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # 认证中间件
    'django.contrib.messages.middleware.MessageMiddleware',  # 消息中间件
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # 防止点击劫持
]

# URL 配置
ROOT_URLCONF = 'projectname.urls'

# 模板配置
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI 應用程式
WSGI_APPLICATION = 'projectname.wsgi.application'



import os
import dj_database_url
import django_heroku 
from urllib.parse import urlparse  

# # 獲取 JawsDB MySQL 環境變數
# DATABASE_URL = os.environ.get('mysql://cqirr0s0uki2q9pk:v5jnro60ihstypom@jsk3f4rbvp8ayd7w.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/ntheuetksr1tyb9l')#, 'mysql://root:1234@127.0.0.1:3306/travel'
# # 解析資料庫 URL
# db_info = urlparse(DATABASE_URL)

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': db_info.path.strip('/'),
#         'USER': db_info.username,
#         'PASSWORD': db_info.password,
#         'HOST': db_info.hostname,
#         'PORT': db_info.port or '3306',
#         'OPTIONS': {
#             'charset': 'utf8mb4',
#             'use_unicode': True,
#             'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#             'collation': 'utf8mb4_unicode_ci',
#         },
#     }
# }
DATABASES = { 
    'default': { 
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'ntheuetksr1tyb9l', 
        'USER': 'cqirr0s0uki2q9pk', 
        'PASSWORD': 'v5jnro60ihstypom', 
        'HOST': 'jsk3f4rbvp8ayd7w.cbetxkdyhwsb.us-east-1.rds.amazonaws.com', 
        'PORT': '3306',
        # 'OPTIONS': {
        #     'ssl': False,
        #     # 'ssl': {'ca': '/path/to/ca-cert.pem'},
        # }, 
    } 
} 
# if os.environ.get('DEVELOPMENT'):
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.mysql',
#             'NAME': 'travel',
#             'USER': 'root',
#             'PASSWORD': '1234',
#             'HOST': '127.0.0.1',
#             'PORT': '3306',
#             'OPTIONS': {
#                     'charset': 'utf8mb4',
#                     'use_unicode': True,
#                     'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#                     'collation': 'utf8mb4_unicode_ci',
#                 },
#         }
#     }

# 筆記：要用local的MySQL處理編碼問題-- 需在 MySQL 中執行
# DROP DATABASE your_database_name;
# CREATE DATABASE your_database_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# django_heroku.settings(locals()) 
# # # 默认情况下使用 SQLite 数据库
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# # 如果 DATABASE_URL 存在且不是 SQLite，则使用 dj_database_url 配置 PostgreSQL
# if 'DATABASE_URL' in os.environ:
#     DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=False)




# 密碼驗證
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# 國際化設置
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# 靜態檔案設置
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# 媒體文件設置
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# 指定主鍵類型
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 郵件設置
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'a6020820914@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'myef kcph eyil qppk')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Jazzmin 设置
JAZZMIN_SETTINGS = {
    'site_title': 'Library Admin',
    'site_header': 'Library',
    'site_brand': '管理者頁面',
    'site_logo': 'travel.wed_logo.png',
    'site_logo_classes': 'img-responsive logo-custom-size',
    'welcome_sign': 'Welcome to the library',
    'copyright': 'Acme Library Ltd',
    'search_model': ['members.Member', 'auth.Group'],
    'user_avatar': None,
    'logo_size': {
        'max_width': 150,
        'height': 'auto',
    },
    'topmenu_links': [
        {'name': 'Home', 'url': 'admin:index', 'permissions': ['auth.view_user']},
        {'name': 'Support', 'url': 'https://github.com/farridav/django-jazzmin/issues', 'new_window': True},
        {'model': 'members.Member'},
    ],
    'usermenu_links': [
        {'name': 'Support', 'url': 'https://github.com/farridav/django-jazzmin/issues', 'new_window': True},
        {'model': 'members.Member'}
    ],
    'show_sidebar': True,
    'navigation_expanded': True,
    'order_with_respect_to': ['auth'],
    'custom_links': {
        'books': [{
            'name': 'Make Messages',
            'url': 'make_messages',
            'icon': 'fas fa-comments',
            'permissions': ['books.view_book']
        }]
    },
    'icons': {
        'auth': 'fas fa-users-cog',
        'members.Member': 'fas fa-user',
        'auth.Group': 'fas fa-users',
    },
    'default_icon_parents': 'fas fa-chevron-circle-right',
    'default_icon_children': 'fas fa-circle',
    'changeform_format': 'horizontal_tabs',
    'changeform_format_overrides': {'members.Member': 'collapsible', 'auth.group': 'vertical_tabs'},
    'language_chooser': True,
}

# 語言設置
LANGUAGES = [
    ('en', 'English'),
    ('zh-hant', 'Traditional Chinese'),
]



AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',  # Google
    'social_core.backends.facebook.FacebookOAuth2',  # Facebook
    # Other authentication backends
    'django.contrib.auth.backends.ModelBackend',
)

import environ

# 初始化环境变量
env = environ.Env()
environ.Env.read_env()  # 从 .env 文件中读取环境变量

LOGIN_URL = 'login'
LOGOUT_URL = 'logout'

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
import os
#SOCIAL_AUTH_GOOGLE_OAUTH2_REDIRECT_URI = 'http://127.0.0.1:8000/social-auth/complete/google-oauth2/'
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('GOOGLE_OAUTH2_CLIENT_ID')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('GOOGLE_OAUTH2_CLIENT_SECRET')
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/profile/'


SOCIAL_AUTH_FACEBOOK_KEY = os.getenv('FACEBOOK_KEY')
SOCIAL_AUTH_FACEBOOK_SECRET = os.getenv('FACEBOOK_SECRET')


SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'projectname.pipeline.associate_by_email',  # 自定义 pipeline 路径
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)


{
    "python.pythonPath": "Scripts\\python.exe",
    "python.linting.enabled": True,
    "python.linting.pylintEnabled": True,
    "python.linting.pylintArgs": [
        "--load-plugins=pylint_django",
    ],
    "files.trimTrailingWhitespace": True, #儲存的時候，會幫你自動過濾多餘的空格
    "files.autoSave": "onFocusChange", #是否自動儲存檔案
    "[python]":{
        "editor.formatOnType": True,
        "editor.formatOnSave": True,
        "editor.renderIndentGuides": True,
        "editor.insertSpaces": True,
        "editor.detectIndentation": True,
        "editor.tabSize": 4,
        "editor.guides.indentation": True
    },
}

#travel-delight
import django_heroku
django_heroku.settings(locals())