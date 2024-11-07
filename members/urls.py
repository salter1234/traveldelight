from django.contrib.auth import views as auth_views
from django.urls import include, path
from . import views  # 导入views模块
from .views import order, orders, delete_order
from .views import delete_profile_view, make_messages_view, AuthorListView, add_member  # 导入你的视图
from social_django import views as social_views
from django.views.generic import TemplateView
from django.urls import re_path as url
from .views import order_ticket
from .views import order_train
from .linebot import callback 
from . import linebot
urlpatterns = [
    #首頁
    path("", views.index, name='index'),

    # 用户注册和登录相关路径
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.LogoutView.as_view(next_page='/'), name='logout'),

    # 账户激活相关路径
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate_account'),
    path('signup_success/', views.signup_success_view, name='signup_success'),  # 注册成功页面
    path('activation_invalid/', views.activation_invalid_view, name='activation_invalid'),  # 激活无效页面

    # 用户资料和编辑
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/delete/', delete_profile_view, name='delete_profile'),  # 删除用户资料

    # 重置密码
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # 会员管理
    path('members/delete/<int:user_id>/', views.delete_member, name='delete_member'),
    path('make_messages/', make_messages_view, name='make_messages'),
    
    # 管理员添加会员的路径
    path('admin/add_member/', add_member, name='add_member'),  
    
    #第三方登入
    path('social-auth/', include('social_django.urls', namespace='social')),  # 添加这一行
    path('facebook/login/', social_views.login, name='facebook_login'),  # 这里是 facebook_login
    path('facebook/login/callback/', social_views.complete, name='facebook_callback'),  # 这里是 callback
    
    #關於
    path('about/', views.about, name='about'), #關於我們
    #加入收藏清單
    path('favorites/', views.my_favorites, name='my_favorites'),
    path('add-to-favorites/<int:tour_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('favorites/remove/<int:tour_id>/', views.remove_favorite, name='remove_favorite'),

    #旅遊行程
    path('tours/', views.tours, name='tours'),
    path('tourDetail/<int:tour_id>', views.tourDetail, name='tourDetail'),

    #旅遊資訊
    path('index/more/', views.travel_more, name='travel_more'),  # 熱門景點介紹
    path('index/more/<str:more_name>', views.more_list, name='more_list'), #熱門景點介紹網頁內容
    path("introduce/", views.travel_introduce, name='introduce'), # 景點介紹網頁
    path('introduce/<str:spot_name>/', views.spot_list, name='spot_list'), #景點介紹網頁內容
    path("fetch_weather/", views.fetch_weather, name='fetch_weather'), #抓取天氣

    # 購物車部分
    path("order/<int:tour_id>", views.order, name='order'),
    path('order_confirmation/<int:order_id>', views.order_confirmation, name='order_confirmation'),
    path('orders/', orders, name='orders'),
    path('orders/delete/<int:order_id>/', delete_order, name='delete_order'),
    path('orders/delete/ticket/<int:ticket_id>/', views.delete_ticket, name='delete_ticket'),
    # path('check_task_status/<str:task_id>/', views.check_task_status, name='check_task_status'),
    # path('save_booking_info/<str:task_id>/', views.save_booking_info, name='save_booking_info'),
    #評論
    path('edit_rating/<int:rating_id>/', views.edit_rating, name='edit_rating'),
    path('delete_rating/<int:rating_id>/', views.delete_rating, name='delete_rating'),
    path('update_rating/', views.update_rating, name='update_rating'),
    
    #linebot
    path('callback/', linebot.callback, name='callback'),

    # 評分部分
    # path('rating/', views.rating, name='rate'),  # rating
    # path('show_rating/', views.show_rating, name='show_rating'),

    #台鐵訂票
    # path('index/', views.index, name='index'),
    # path('schedule_view/', views.schedule_view, name='schedule_view'),
    path('order_ticket/', views.order_ticket, name='order_ticket'),  #這沒有用到任何html頁面，直接存ticket object之後，直接跳轉到order_view
    path('order_view/<int:ticket_id>/', views.order_view, name='order_view'),  # 原本的schedule_form，我一致一下名稱，不然有點混亂
    path('order_train/', order_train, name='order_train'),
    
]

# from django.contrib.auth import get_user_model

# User = get_user_model()
# User.objects.filter(email='s7262370@gmail.com').delete()

# from members.models import Tour, Site, Company, Region
# Tour.objects.filter(company=4).delete()

#批次載入資料
#heroku run python manage.py loaddata fixture_batch_15.json
#heroku run python manage.py loaddata --exclude contenttypes fixture_batch_15.json