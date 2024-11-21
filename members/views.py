import os
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, get_user_model, views as auth_views
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from .forms import MemberSignUpForm, MemberProfileForm, MemberForm
from django.views.generic import ListView
from .models import Member, MemberProfile  
from django.urls import reverse
from datetime import datetime
from dateutil.relativedelta import relativedelta

# 日誌記錄設置
logger = logging.getLogger(__name__)
User = get_user_model()

#首頁index.html
def index(request):
    # 初始設定
    tour_toursite = None 
    tour_tourday = [1, 2, 3, 4]
    tour_company_ids = [1, 2, 3, 4]
    options = None
    startDate = datetime.today().date()
    endDate = datetime.today().date()-relativedelta(months=-2)

    form = DateWhereForm(initial={
        'startDate':startDate,
        'endDate':endDate,
        'seleSite': tour_toursite,
        'day': tour_tourday,
        'comp': tour_company_ids,
        'option': options
    })
    return render(request,"index.html",{'form':form})

# 示例的 ListView
class AuthorListView(ListView):
    model = Member
    template_name = 'member_list.html'  # 你需要创建这个模板

# 邮件发送函数
def send_activation_email(user, request):
    current_site = get_current_site(request)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = token_generator.make_token(user)
    activate_url = reverse('activate_account', kwargs={'uidb64': uid, 'token': token})
    full_url = f"http://{current_site.domain}{activate_url}"

    # 渲染HTML模板
    html_content = render_to_string('activation_email.html', {
        'user': user,
        'full_url': full_url,
    })
    text_content = f"Hi {user.username},\n\nPlease activate your account by clicking the link below:\n{full_url}"

    subject = 'Activate Your Account - Welcome!'
    from_email = 'dusum1129@gmail.com'  # 请更改为有效的发件人邮箱
    recipient_list = [user.email]

    email = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
    email.attach_alternative(html_content, "text/html")

    try:
        email.send()
        print(f"Activation email sent to {user.email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# 注册视图
def signup_view(request):
    if request.method == 'POST':
        form = MemberSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # 用户未激活
            user.save()

            # 发送激活邮件
            send_activation_email(user, request)
            MemberProfile.objects.create(user=user)  # 创建 MemberProfile 实例

            messages.success(request, '註冊成功！請檢查您的電子郵件並激活帳戶。')
            return redirect('login')
    else:
        form = MemberSignUpForm()
    return render(request, 'signup.html', {'form': form})

# 登录视图
def login_view(request):
    # 清除之前的所有消息
    messages.get_messages(request).used = True  # 清除消息

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user:
                login(request, user)
                messages.success(request, '登入成功！')
                return redirect('index')
            else:
                messages.error(request, '用戶名或密碼錯誤。')
        else:
            messages.error(request, '表單無效，請檢查輸入内容。')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

class LogoutView(auth_views.LogoutView):
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, "You have successfully logged out.")
        return super().dispatch(request, *args, **kwargs)

# 用户资料视图
@login_required
def profile_view(request):
    user = request.user
    return render(request, 'profile.html', {'user': user})

# 删除用户资料视图
@login_required
def delete_profile_view(request):
    user_profile = get_object_or_404(MemberProfile, user=request.user)

    # 删除头像文件
    if user_profile.avatar and os.path.isfile(user_profile.avatar.path):
        os.remove(user_profile.avatar.path)

    user_profile.delete()  # 刪除用戶資料
    messages.success(request, '資料刪除成功！')
    return redirect('profile')  # 或者重定向到其他页面

# 注册成功视图
def signup_success_view(request):
    return render(request, 'signup_success.html')

# 激活链接无效视图
def activation_invalid_view(request):
    return render(request, 'activation_invalid.html')



# 账户激活视图
def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
        logger.error('User activation failed: invalid UID or token.')  # 记录错误日志

    if user and token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'  # 设置 backend 属性
        login(request, user)  # 激活成功后自动登录
        messages.success(request, '帳戶激活成功！')
        return redirect('index')
    else:
        messages.error(request, '激活連結無效或已過期。')
        logger.warning('Activation link is invalid or expired for user: %s', uid)  # 记录警告日志
        return render(request, 'activation_invalid.html')

@login_required
def profile_edit_view(request):
    # 如果用户的 MemberProfile 不存在，则创建它
    user_profile, created = MemberProfile.objects.get_or_create(user=request.user)

    logger.info(f"Editing profile for user: {request.user.username}")  # 添加调试信息

    if request.method == 'POST':
        form = MemberProfileForm(request.POST, request.FILES, instance=user_profile)

        if form.is_valid():
            # 处理头像删除
            if 'delete_avatar' in request.POST and user_profile.avatar:
                user_profile.avatar.delete(save=False)
                user_profile.avatar = None

            new_avatar = request.FILES.get('avatar')
            if new_avatar:
                user_profile.avatar = new_avatar
            
            form.save()  
            # 更新用户的电子邮件和用户名
            user = request.user
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.save()

            return JsonResponse({"message": "资料更新成功！"}, status=200)  
        else:
            logger.error(f"Form errors: {form.errors}")  # 记录表单错误
            return JsonResponse({"message": "更新失败！", "errors": form.errors}, status=400)

    else:
        form = MemberProfileForm(instance=user_profile, user=request.user)

    return render(request, 'profile_edit.html', {'form': form, 'user_profile': user_profile})


# 检查用户是否是管理员的自定义装饰器
def is_admin(user):
    return user.is_staff  # 确保用户具有管理员权限

@user_passes_test(is_admin)  # 仅限管理员使用此功能
def delete_member(request, user_id):
    """删除指定的用户并返回管理会员页面"""
    user = get_object_or_404(User, id=user_id)  # 获取用户或返回404
    user.delete()  # 删除用户
    messages.success(request, "会员已成功删除！")  # 显示成功消息
    return redirect('manage_members')  # 重定向到管理会员页面

@user_passes_test(is_admin)  # 仅限管理员使用此功能
def manage_members(request):
    """显示所有会员的管理页面"""
    members = User.objects.all()  # 获取所有用户
    return render(request, 'admin/members/manage_members.html', {'members': members})  # 渲染模板

def make_messages_view(request):
    # 处理逻辑
    return render(request, 'template_name.html')

def add_new_member(request):  # 重命名函数以避免冲突
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin')  # 替换为你希望重定向的 URL
    else:
        form = MemberForm()
    
    return render(request, 'add_member.html', {'form': form})

@user_passes_test(lambda u: u.is_superuser)  # 或者根据你的需求定义更复杂的权限
def add_member(request):  # 如果需要保留这个功能，确保它有独特的用途
    # 您可以在这里实现添加会员的逻辑
    pass

from django.http import HttpResponseNotAllowed

def my_view(request):
    if request.method == 'GET':
        # 处理 GET 请求
        return HttpResponse('This is a GET response.')
    elif request.method == 'POST':
        # 处理 POST 请求
        return HttpResponse('This is a POST response.')
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])


from social_core.exceptions import MissingBackend

def social_login(request, backend):
    try:
        user = request.user
        if user.is_authenticated:
            # 检查用户是否已有 MemberProfile，如果没有则创建
            if not MemberProfile.objects.filter(user=user).exists():
                MemberProfile.objects.create(user=user)
            
            return redirect('index')

        # 使用 social_django 处理社交认证
        response = request.backend.complete(user=user)
        if response:
            # 登录用户
            login(request, response.user)

            # 检查并创建 MemberProfile（若无）
            if not MemberProfile.objects.filter(user=response.user).exists():
                MemberProfile.objects.create(user=response.user)

            return redirect('index')

    except MissingBackend:
        # 处理错误，用户邮箱可能已经存在或其他问题
        return redirect('login')

def complete_google_login(request):
    backend = request.GET.get('backend')
    response = get_google_user_data(request)  # 获取用户数据的函数
    email = response.get('email')

    # 检查用户是否已存在
    try:
        user = Member.objects.get(email=email)
        login(request, user)  # 登录用户
    except Member.DoesNotExist:
        # 创建新用户的逻辑
        new_user = Member(
            email=email,
            username=response.get('username', email.split('@')[0]),  # 确保有一个用户名
            # 添加其他必需的字段
        )
        new_user.save()
        login(request, new_user)

    return redirect('index')  # 重定向到主页或其他地方

from .recommendation import get_recommendations
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from .models import FavoriteTrip
def my_favorites(request):
    if request.user.is_authenticated:
        favorites = FavoriteTrip.objects.filter(user=request.user)

        # 提取用户的收藏行程 IDs
        tour_ids = [favorite.tour.id for favorite in favorites]
        print("Tour IDs:", tour_ids)  # 确认提取的 tour_ids

        # 调用 get_recommendations 函数并传递 user 和 tour_ids
        recommendations = get_recommendations(request.user)

        return render(request, 'my_favorites.html', {'favorites': favorites, 'recommendations': recommendations})

    return redirect('login')  # 如果未登录则重定向

def add_to_favorites(request, tour_id):
    if request.user.is_authenticated:
        tour = get_object_or_404(Tour, id=tour_id)
        FavoriteTrip.objects.get_or_create(user=request.user, tour=tour)
        return redirect('my_favorites')  # 或者重定向到其他页面
    return redirect('login')  # 未登录用户重定向到登录页面


from .models import FavoriteTrip, Tour, Favorite
from .recommendation import hybrid_recommendation
#機器學習回傳推薦
from .models import Tour 
from decimal import Decimal


def remove_favorite(request, tour_id):
    if request.method == 'POST':
        tour = get_object_or_404(Tour, id=tour_id)
        FavoriteTrip.objects.filter(user=request.user, tour=tour).delete()
        return redirect('my_favorites')  # 重定向到收藏页面

def recommend_view(request, user_id):
    recommendations = hybrid_recommendation(user_id)
    context = {'recommendations': recommendations}
    return render(request, 'recommendations.html', context)

def favorite_tours(request):
    # 用戶收藏的行程
    favorites = Favorite.objects.filter(user=request.user)

    # 推薦的行程
    recommendations = Tour.objects.exclude(id__in=[f.tour.id for f in favorites])[:6]

    return render(request, 'toursearch.html', {
        'favorites': favorites,
        'recommendations': recommendations
    })

"""
by 芷翎(旅遊行程) 正融(使用者評論)
"""
from django.shortcuts import render, redirect, get_object_or_404
from .models import Site, Company, Tour
from .forms import DateWhereForm
from .search import searchTour
from django.core.paginator import Paginator
from django.http import HttpResponse
import math
import calendar

#Tours旅遊行程呈現
def tours(request, n=1):
    #旅遊行程搜尋初始化條件
    tours = Tour.objects.all()
    tour_toursite = None
    tour_tourday = [1, 2, 3, 4]
    tour_company_ids = ['雄獅旅遊', '五福旅遊', '東南旅遊', '易遊網']
    options = None
    startDate=datetime.today().date()
    endDate=datetime.today().date()-relativedelta(months=-2)
    #接收搜尋表單資料
    if request.method == 'POST':
        form = DateWhereForm(request.POST)
        if form.is_valid():
            #將表單結果存在變數
            startDate=form.cleaned_data.get('firstDate')
            endDate=form.cleaned_data.get('lastDate')
            tour_toursite = form.cleaned_data.get('seleSite')
            tour_tourday = form.cleaned_data.get('day') if form.cleaned_data.get('day') else None
            tour_company_names = form.cleaned_data.get('comp')
            options = form.cleaned_data.get('option')

            #轉換tour_company_names成對應的tour_company_ids
            tour_company_ids = [str(i) for i in list(tour_company_names.values_list('id', flat=True))]

            #初始化點選form之後的頁數
            n = 1
    else:
    #GET.get回傳搜尋條件，讓使用者再點選page時，tour objects篩選結果能相同
        #GET.get抓取頁數        
        n = int(request.GET.get('page', 1))
        #GET.get抓取起始日期
        startDate = request.GET.get('firstDate', datetime.today().date())
        #GET.get抓取結束日期
        endDate = request.GET.get('lastDate', datetime.today().date()-relativedelta(months=-2))
        #str轉換成datetime.date
        if isinstance(startDate, type("")):
            startDate=datetime.strptime(startDate.replace("年", "-").replace("月", "-").replace("日", ""),"%Y-%m-%d").date()
            endDate=datetime.strptime(endDate.replace("年", "-").replace("月", "-").replace("日", ""),"%Y-%m-%d").date()        
        else:
            startDate=startDate
            endDate=endDate 
        #GET.get抓取目的地
        tour_toursite = request.GET.get('seleSite', '')
            #判斷是否轉換變數值，須轉為數字
        if tour_toursite.isdigit():
            tour_toursite = tour_toursite
        else:
            try:
                site = Site.objects.get(site_name=tour_toursite)
            except Site.DoesNotExist:
                site = None
            tour_toursite= site.id if site else None
        #GET.get抓取旅遊天數
        tour_tourday = request.GET.get('day', '').split(',') if request.GET.get('day') else [1, 2, 3, 4]
        #GET.get抓取旅遊公司
        tour_company_names = request.GET.get('comp', '').split(',') if request.GET.get('comp') else ['雄獅旅遊','五福旅遊','東南旅遊','易遊網']
            #判斷是否轉換變數值，須轉為數字
        if tour_company_names[0].isdigit():
            tour_company_ids=tour_company_names
        else:
            tour_company_ids = Company.objects.filter(company_name__in=tour_company_names).values_list('id', flat=True)
        #GET.get抓取排序
        options = request.GET.get('option', None)  
    #將抓取的結果回傳給表單，讓翻頁的時候能保留POST搜尋結果
        form = DateWhereForm(initial={
            'startDate':startDate,
            'endDate':endDate,
            'seleSite': tour_toursite,
            'day': tour_tourday,
            'comp': tour_company_ids,
            'option': options
        })
    try:
    #搜尋功能篩選function
        tours = searchTour(startDate, endDate, tour_toursite, tour_tourday, tour_company_ids, options)
    #分頁器Paginator
        paginator = Paginator(tours, per_page=24) #一個分頁呈現24個行程的Paginator物件
        page_obj = paginator.get_page(n) #第n個Paginator物件
        #前端呈現頁數所需的變數
        num=[i for i in range(1, page_obj.paginator.num_pages + 1)] #所有頁數的list
        num0=num[:11] # num_pages < 11
        num1=num[(page_obj.paginator.num_pages-10):page_obj.paginator.num_pages] #當前頁數+5已經超過總頁數的時候用
        num2=num[(page_obj.number-5):(page_obj.number+5)] #當前頁數+5尚未超過總頁數的時候用
        nowpageadd5=page_obj.number+5 #目前頁數+5
    except:
        #搜尋公司或天數條件為None時的預設值
        page_obj='None'
        paginator='None'
        num=[1]
        num0=[1]
        num1=[1]
        num2=[1]
        nowpageadd5=1

    return render(request, 'toursearch.html', {'tours': tours,'form': form, #行程和表單呈現
        'page_obj': page_obj, 'nowpageadd5':nowpageadd5,'page': n,    #頁數呈現   
        'num0':num0, 'num1':num1, 'num2':num2,'paginator': paginator,
        'tour_toursite': tour_toursite,'tour_tourday': tour_tourday, #搜尋條件變數傳遞
        'startDate':startDate,'tour_company_ids': tour_company_ids, 
        'endDate':endDate,'options': options,
    })

from .models import Rating
from .forms import RatingForm

#Tours旅遊行程呈現
def tourDetail(request, tour_id):
    if request.method == 'POST':
        if request.user.is_authenticated:
            # 下評分
            form = RatingForm(request.POST)
            if form.is_valid():
                # Save the rating to the database (optional)
                user_name = request.user
                tour= get_object_or_404(Tour, id=tour_id)
                rating_value = form.cleaned_data['value']
                comment = form.cleaned_data['comment']
                rating=Rating.objects.create(user_name=user_name, tour=tour, value=rating_value, comment=comment)  # Optional
                rating.save()
                # messages.success(request, 'Form submitted successfully!')
                # return redirect('show_rating')
        else:
            return redirect('login')
    else:
        # 評分表
        form = RatingForm()
    tour = get_object_or_404(Tour, id=tour_id)
    Day = tour.day.lstrip('[').rstrip(']').split(',')
    TravelPoint = tour.travelPoint.lstrip('[').rstrip(']').replace("'", "").split(',')
    Breakfast = tour.breakfast.lstrip('[').rstrip(']').replace("'", "").split(',')
    Lunch = tour.lunch.lstrip('[').rstrip(']').replace("'", "").split(',')
    Dinner = tour.dinner.lstrip('[').rstrip(']').replace("'", "").split(',')
    Hotel = tour.hotel.lstrip('[').rstrip(']').replace("'", "").split(',')
    godate=tour.goDate.lstrip('[').rstrip(']').replace("'", "").replace("/", "-").replace(" ", "").split(',')
                
    # 獲取評分與評語
    ratings = Rating.objects.filter(tour=tour_id)
    return render(request, 'tourdetail.html', {'tour':tour, 'Day':Day, 'earlierGoDate':tour.earlierGoDate,
                                               'TravelPoint':TravelPoint, 'godate':godate,
                                               'Breakfast':Breakfast, 'Lunch':Lunch,
                                               'Dinner':Dinner, 'Hotel':Hotel,
                                               'form': form, 'userName':request.user, 'ratings':ratings})#

"""
by 正融(使用者評論)
"""
from .models import Rating
from .forms import RatingForm


"""
by 庚庭、家澤(旅遊資訊+首頁)
"""

def fetch_weather(request):
    if request.method == 'POST':
        all_weather_data = fetch_weather_data()
        tour_toursite = None
        tour_tourday = [1, 2, 3, 4]
        tour_company_ids = [1, 2, 3, 4]
        options = None
        startDate = datetime.today().date()
        endDate = datetime.today().date()-relativedelta(months=-2)

        form = DateWhereForm(initial={
            'startDate':startDate,
            'endDate':endDate,
            'seleSite': tour_toursite,
            'day': tour_tourday,
            'comp': tour_company_ids,
            'option': options
    })
        return render(request, "index.html", {'weather_data': all_weather_data, 'form':form})
    else:
        return redirect('index')

def travel_more(request):
    return render(request,"more.html",{})

def get_more_spots():
    return [
        {"name": "台北", "url": "county/Taipei.html"},
        {"name": "新北", "url": "county/NewTaipei.html"},
        {"name": "基隆", "url": "county/Keelung.html"},
        {"name": "新竹", "url": "county/Hsinchu.html"},
        {"name": "桃園", "url": "county/Taoyuan.html"},
        {"name": "苗栗", "url": "county/Miaoli.html"},
        {"name": "台中", "url": "county/Taichung.html"},
        {"name": "彰化", "url": "county/Changhua.html"},
        {"name": "南投", "url": "county/nantou.html"},
        {"name": "雲林", "url": "county/Yunlin.html"},
        {"name": "嘉義", "url": "county/Chiayi.html"},
        {"name": "台南", "url": "county/Tainan.html"},
        {"name": "高雄", "url": "county/Kaohsiung.html"},
        {"name": "屏東", "url": "county/Pingtung.html"},
        {"name": "宜蘭", "url": "county/Yilan.html"},
        {"name": "台東", "url": "county/Taitung.html"},
        {"name": "花蓮", "url": "county/Hualien.html"},
        {"name": "澎湖", "url": "county/Penghu.html"},
        {"name": "金門", "url": "county/kinmen.html"},
        {"name": "馬祖", "url": "county/Mazu.html"},
        ]

def more_list(request, more_name):
    spots = get_more_spots()
    spot = next((s for s in spots if s["name"] == more_name), None)  # 查找特定的景点


    if spot:
        template_name = spot["url"]
    else:
        template_name = 'more/default.html'

    return render(request, template_name, {'spots': spots,})

def search_results(request):
    departure = request.GET.get('departure')
    destination = request.GET.get('destination')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # 在這裡進行資料處理或查詢

    context = {
        'departure': departure,
        'destination': destination,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'search.html', context)

def travel_introduce(request):
    return render(request,"introduce.html",{})

def get_spots():
    return [
        {"name": "阿里山國家森林遊樂區", "url": "travel/alishan.html", "city": "嘉義縣"},
        {"name": "朝日溫泉", "url": "travel/asahi.html", "city": "台東縣"},
        {"name": "澎湖縣白沙鄉通梁村", "url": "travel/baisha.html", "city": "澎湖縣"},
        {"name": "馬祖北海坑道", "url": "travel/beauty.html", "city": "連江縣"},
        {"name": "北港朝天宮", "url": "travel/beigang.html", "city": "雲林縣"},
        {"name": "馬祖北海坑道", "url": "travel/beihai.html", "city": "連江縣"},
        {"name": "綠島柴口浮潛區", "url": "travel/chaikou.html", "city": "台東縣"},
        {"name": "成美文化園區", "url": "travel/chengmei.html", "city": "彰化縣"},
        {"name": "清境農場", "url": "travel/cingjing.html", "city": "南投縣"},
        {"name": "小琉球蛤板灣", "url": "travel/clam.html", "city": "屏東縣"},
        {"name": "澄清湖風景區", "url": "travel/clarification.html", "city": "屏東縣"},
        {"name": "大溪老街", "url": "travel/daxistreet.html", "city": "桃園市"},
        {"name": "斗六膨鼠森林公園", "url": "travel/douliu.html", "city": "雲林縣"},
        {"name": "台中異想新樂園", "url": "travel/fantasyland.html", "city": "台中市"},
        {"name": "奮起湖老街", "url": "travel/fenchihu.html", "city": "嘉義縣"},
        {"name": "飛牛牧場", "url": "travel/flyingcow.html", "city": "苗栗縣"},
        {"name": "嘉義蓋婭莊園", "url": "travel/gaia.html", "city": "嘉義縣"},
        {"name": "綠世界生態農場", "url": "travel/green.html", "city": "新竹縣"},
        {"name": "彰化穀堡園區", "url": "travel/gubao.html", "city": "彰化縣"},
        {"name": "古寧頭戰史館", "url": "travel/guningtou.html", "city": "金門縣"},
        {"name": "馬祖鐵堡", "url": "travel/iron.html", "city": "連江縣"},
        {"name": "陳景蘭洋樓", "url": "travel/Jinglan.html", "city": "金門縣"},
        {"name": "馬祖津沙聚落", "url": "travel/Jinsha.html", "city": "連江縣"},
        {"name": "九份", "url": "travel/Jiufen.html", "city": "新北市"},
        {"name": "墾丁國家公園", "url": "travel/kenting.html", "city": "屏東縣"},
        {"name": "知本國家森林遊樂區", "url": "travel/knowledge.html", "city": "台東縣"},
        {"name": "六福村主題遊樂園", "url": "travel/leofoo.html", "city": "新竹縣"},
        {"name": "綠島燈塔", "url": "travel/lighthouse.html", "city": "台東縣"},
        {"name": "蘭嶼雙獅岩", "url": "travel/lion.html", "city": "台東縣"},
        {"name": "龍磐公園", "url": "travel/longpan.html", "city": "屏東縣"},
        {"name": "龍騰斷橋", "url": "travel/longteng.html", "city": "苗栗縣"},
        {"name": "蘭嶼情人洞", "url": "travel/loverscave.html", "city": "台東縣"},
        {"name": "鹿野高台", "url": "travel/luye.html", "city": "台東縣"},
        {"name": "澎湖大菓葉柱狀玄武岩", "url": "travel/macrocarpa.html", "city": "澎湖縣"},
        {"name": "梅花湖", "url": "travel/meihua.html", "city": "新竹縣"},
        {"name": "基隆廟口夜市", "url": "travel/miaokou.html", "city": "台中市"},
        {"name": "金門模範街", "url": "travel/modelstreet.html", "city": "台南市"},
        {"name": "奎壁山摩西分海", "url": "travel/moses.html", "city": "南投縣"},
        {"name": "南寮漁港", "url": "travel/nanliao.html", "city": "新竹縣"},
        {"name": "南庄老街", "url": "travel/nanzhuang.html", "city": "苗栗縣"},
        {"name": "國立自然科學博物館", "url": "travel/nature.html", "city": "台北市"},
        {"name": "九族文化村", "url": "travel/ninetribes.html", "city": "南投縣"},
        {"name": "遠雄海洋公園", "url": "travel/ocean.html", "city": "澎湖縣"},
        {"name": "和平島地質公園", "url": "travel/peaceisland.html", "city": "基隆市"},
        {"name": "埔心牧場", "url": "travel/puxin.html", "city": "南投縣"},
        {"name": "砂卡礑步道", "url": "travel/shakadang.html", "city": "花蓮縣"},
        {"name": "平溪", "url": "travel/skylantern.html", "city": "台南市"},
        {"name": "小琉球落日亭", "url": "travel/sunset.html", "city": "台南市"},
        {"name": "西門町", "url": "travel/taipei.html", "city": "臺北市"},
        {"name": "台北市立動物園", "url": "travel/taipei_zoo.html", "city": "臺北市"},
        {"name": "太魯閣國家公園", "url": "travel/taroko.html", "city": "花蓮縣"},
        {"name": "田寮月世界", "url": "travel/tianliao.html", "city": "台南市"},
        {"name": "富岡地質公園", "url": "travel/tomioka.html", "city": "台中市"},
        {"name": "傳統藝術中心", "url": "travel/traditional.html", "city": "台北市"},
        {"name": "勝利星村創意生活園區", "url": "travel/victory.html", "city": "高雄市"},
        {"name": "望幽谷", "url": "travel/wangyou.html", "city": "台北市"},
        {"name": "蘭嶼氣象站", "url": "travel/weather.html", "city": "台北市"},
        {"name": "宜蘭五峰旗瀑布", "url": "travel/wufeng.html", "city": "台中市"},
        {"name": "武陵農場", "url": "travel/wuling.html", "city": "台中市"},
        {"name": "彰化溪湖糖廠", "url": "travel/xihu.html", "city": "南投縣"},
        {"name": "溪頭自然教育園區", "url": "travel/xitou.html", "city": "南投縣"},
        {"name": "Xpark", "url": "travel/xpark.html", "city": "新北市"},
        {"name": "陽明山國家公園", "url": "travel/yangmin.html", "city": "台北市"},
        {"name": "野柳", "url": "travel/yeliu.html", "city": "新北市"},
        {"name": "雲嶺之丘", "url": "travel/yunling.html", "city": "雲林縣"},
        {"name": "棧貳庫KW", "url": "travel/zhanerkukw.html", "city": "台北市"}
    ]

def spot_list(request, spot_name):
    spots = get_spots()  # 获取景点数据
    spot = next((s for s in spots if s["name"] == spot_name), None)  # 查找特定的景点

    all_weather_data = []

    if spot:
        template_name = spot["url"]  # 如果找到景点，返回对应的模板
    else:
        template_name = 'travel/default.html'  # 找不到时返回默认模板

    return render(request, template_name, {'spots': spots})


def fetch_weather_data():
    from bs4 import BeautifulSoup
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    weather_urls = []
    weather_data_list = []
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 啟用無頭模式
    options.add_argument('--disable-gpu')  # 在無頭模式下禁用 GPU 加速（可選）
    options.add_argument('--no-sandbox')  # 確保無沙盒環境（Linux 系統常用）
    options.add_argument('--disable-dev-shm-usage')  # 避免資源限制錯誤

    #heroku需要的設置
    from selenium.webdriver.chrome.service import Service
    service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))

    driver = webdriver.Chrome(service=service, options=options)
    url = 'https://www.cwa.gov.tw/V8/C/W/County/index.html'
    driver.get(url)

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'span.datetime.text-center')))
    pageSource = driver.page_source

    soup = BeautifulSoup(pageSource,'html.parser')
    citys = soup.select('ol#town > li > a > span.city')
    a = soup.select('ol#town > li >a')
    for index, (hrefs, city) in enumerate(zip(a, citys)):
        href = hrefs.get('href')
        new_url = f"https://www.cwa.gov.tw/{href}"
        weather_urls.append({
                        'citys':city.text,
                        'url' : new_url
                        })


    for weather in weather_urls:
        driver.get(weather['url'])
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".to-to"))
        )
        weather_data = driver.find_elements(By.CSS_SELECTOR, ".to-to")
        weather_title = driver.find_elements(By.CSS_SELECTOR, ".main-title")

        for weather_element, weather_title_element in zip(weather_data, weather_title):
            weather_title = weather_title_element.text
            weather_info = weather_element.text.split('\n')
            if len(weather_info) >= 8:
                weather_data_list.append({
                'title':weather_title,
                'time': weather_info[0],
                'temperature': weather_info[1],
                'rain_chance': weather_info[3],
                'comfort': weather_info[4],
                'next_time': weather_info[5],
                'next_temperature': weather_info[6],
                'next_rain_chance': weather_info[8],
                'next_comfort': weather_info[9],
                'next2_time': weather_info[10],
                'next2_temperature': weather_info[11],
                'next2_rain_chance': weather_info[13],
                'next2_comfort': weather_info[14]
            })

    driver.quit()
    return weather_data_list

def about(request):
    return render(request, 'about.html')

from .models import TourOrder
from django.views.decorators.csrf import csrf_exempt

#評論編輯
@login_required
def edit_rating(request, rating_id):
    rating = get_object_or_404(Rating, id=rating_id)

    if request.method == 'POST':
        rating.value = request.POST.get('value')
        rating.comment = request.POST.get('comment')
        rating.save()

        # 確保保存後刷新頁面
        return JsonResponse({'success': True, 'new_comment': rating.comment})

    return render(request, 'edit_rating.html', {'rating': rating})

@login_required
def delete_rating(request, rating_id):
    rating = get_object_or_404(Rating, id=rating_id)

    if request.user != rating.user_name:  # 確保只能刪除自己的評論
        return JsonResponse({'success': False, 'error': '您無權限刪除此評論'}, status=403)

    if request.method == 'POST':
        rating.delete()
        return redirect('tourDetail', tour_id=rating.tour.id)

    return render(request, 'confirm_delete.html', {'rating': rating})


@login_required
def update_rating(request):
    if request.method == 'POST':
        rating_id = request.POST.get('rating_id')
        new_comment = request.POST.get('comment')

        try:
            rating = Rating.objects.get(id=rating_id)

            if request.user != rating.user_name:  # 確保只有評論擁有者可以更新
                return JsonResponse({'success': False, 'error': '您無權限編輯此評論'}, status=403)

            # 更新評論
            rating.comment = new_comment
            rating.save()

            return JsonResponse({
                'success': True,
                'new_comment': new_comment  # 返回更新後的新評論
            })

        except Rating.DoesNotExist:
            return JsonResponse({'success': False, 'error': '評論未找到'}, status=404)

    return JsonResponse({'success': False, 'error': '無效的請求'}, status=400)



#order 部分
from django.core.exceptions import ValidationError
from .models import Tour, TourOrder

# 旅遊行程下訂單頁面
@login_required
def order(request, tour_id):
    # 根據 tour_id 獲取特定旅遊object
    tour = get_object_or_404(Tour, id=tour_id)    
    # 處理日期數據，獲得出團時間list
    godates = tour.goDate.lstrip('[').rstrip(']').replace("'", "").replace("/", "-").replace(" ", "").split(',')
    #獲得使用者選擇的'出發地'和'出發日期'
    if request.method == 'POST':
        user = request.user
        gosite = request.POST.get("gosite")
        godate = request.POST.get("godate")        
    
    # 是否用優惠價判斷
        if godate==tour.earlierGoDate.replace('/', '-'):               
            memberprice=int(tour.price)-math.ceil(int(tour.price)*0.05) # 選擇'最近出發日'95折優惠
        else:                
            memberprice=int(tour.price) # 一般價
    # 創建 TourOrder 對象
        order = TourOrder.objects.create(user=user, tour=tour, gosite=gosite, godate=godate, order_sum=memberprice)
        order.save()
    # 發送旅遊行程訂單郵件
        send_mail(
            subject='您的旅遊訂單已確認',
            message=f'感謝您的訂購！以下是您的訂單資訊：\n\n'
                    f'旅遊行程：{order.tour.tourname}\n'
                    f'旅遊公司：{order.tour.company}\n'
                    f'行程目的地：{order.tour.toursite}\n'
                    f'出發地點：{order.gosite}\n'
                    f'出團日期：{order.godate}\n'
                    f'費用：{order.order_sum}元\n',
            from_email='dusum1129@gmail.com',
            recipient_list=[request.user.email],
        )
        return redirect('order_confirmation', order_id=order.id)  # 定向到旅遊行程訂購完成頁面
    return render(request, 'order.html', {'tour': tour, 'godates': godates})

#旅遊行程訂購完成頁面
@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(TourOrder, id=order_id)
    return render(request, 'order_confirmation.html', {'order':order})


from django.utils import timezone
from .models import TourOrder  

@login_required
def orders(request):
    current_date = timezone.now().date()
    tickets = TicketOrder.objects.filter(user=request.user, departure_time__gte=current_date)
    past_tickets = TicketOrder.objects.filter(user=request.user, departure_time__lt=current_date)
    orders = TourOrder.objects.filter(user=request.user, godate__gte=current_date)
    past_orders = TourOrder.objects.filter(user=request.user, godate__lt=current_date)

    return render(request, 'orders.html', {
        'orders': orders,
        'past_orders': past_orders,
        'tickets':tickets,
        'past_tickets':past_tickets
    })

@login_required  # 確保用戶已登錄才能刪除訂單
def delete_order(request, order_id):
    # 使用 TourOrder 替代 Order
    order = get_object_or_404(TourOrder, id=order_id, user=request.user)
    order.delete()
    return redirect('orders')  # 刪除成功後重定向到訂單頁面

@login_required  # 確保用戶已登錄才能刪除訂單
def delete_ticket(request, ticket_id):
    # 使用 TourOrder 替代 Order
    ticket = get_object_or_404(TicketOrder, id=ticket_id, user=request.user)
    ticket.delete()
    return redirect('orders')  # 刪除成功後重定向到訂單頁面

from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import TourOrder

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import TicketOrder
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from django.shortcuts import render
import re
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import sys
from twocaptcha import TwoCaptcha


# Create your views here.

from django.shortcuts import render

@login_required
def order_train(request):
    if request.method == "POST":
        start_station = request.POST.get('from_station')
        end_station = request.POST.get('to_station')
        ride_date = request.POST.get('travel_date')
        schedules = fetch_train_schedule(start_station, end_station, ride_date)

        return render(request, 'order_train.html', {
            'schedules': schedules,
            'ride_date': ride_date,
            'start_station': start_station,
            'end_station': end_station
        })

    return render(request, "order_train.html")


def fetch_train_schedule(start_station, end_station, ride_date):
    import time
    from datetime import datetime
    import re
    # 初始化 Chrome 瀏覽器
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    #heroku需要的設置
    from selenium.webdriver.chrome.service import Service
    service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))

    driver = webdriver.Chrome(service=service, options=options)

    # 打開台鐵訂票網站
    driver.get("https://www.railway.gov.tw/tra-tip-web/tip/tip001/tip112/gobytime")

    # 填寫出發站、到達站和日期
    driver.find_element(By.ID, "startStation").send_keys(start_station)
    time.sleep(1)
    driver.find_element(By.ID, "endStation").send_keys(end_station)
    time.sleep(1)
    driver.find_element(By.ID, "rideDate").clear()
    Ride_date = datetime.strptime(ride_date, "%Y-%m-%d").strftime("%Y/%m/%d")
    # driver.find_element(By.ID, "rideDate").send_keys(Ride_date)
    driver.execute_script("document.getElementById('rideDate').value = arguments[0];", Ride_date)
    time.sleep(1)

    # 點擊查詢按鈕
    search_btn = driver.find_element(By.CSS_SELECTOR, 'input.btn.btn-3d')
    driver.execute_script("arguments[0].click();", search_btn)

    # 等待結果加載
    driver.implicitly_wait(30)  # 等待最多5秒以加載結果

    # 獲取車次資訊
    schedules = []
    trains = driver.find_elements(By.CSS_SELECTOR, ".trip-column")

    for train in trains:
        train_info = train.text.split('\n')
        line1 = train_info[0]
        train_number = line1[0:]
        from_station = start_station
        to_station = end_station
        line2 = train_info[1]
        departure_time = line2[0:5]
        arrive_time = line2[6:11]
        price=line2[29:33]
        schedule = {
            'train_number': train_number,
            'from_station': from_station,
            'to_station': to_station,
            'departure_time': departure_time,
            'arrive_time': arrive_time,
            'price':price
        }
        schedules.append(schedule)

    # 關閉瀏覽器
    driver.quit()
    return schedules



def solve_recaptcha(site_key, url):#, max_retries=3, delay=10
    import time
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    api_key = os.getenv('APIKEY_2CAPTCHA', "a68ec685f396300fabfa384621ca29b8")
    solver = TwoCaptcha(api_key)

    try:
        result = solver.recaptcha(
            sitekey=site_key,
            url=url
        )
    except Exception as e:
        print(f"CAPTCHA 解決失敗: {e}")
        return None
    else:
        # print(f"solved: {result}")
        return result
   

# def bookingTRA(id, startStation, endStation, trainNoList1, rideDate1):
#     # driver = webdriver.Chrome()
#     user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
#     chrome_options = webdriver.ChromeOptions()
#     # chrome_options.add_argument("--headless=old") #無頭模式
#     chrome_options.add_argument("--headless=old")
#     chrome_options.add_argument("--window-size=1920,1080")
#     chrome_options.add_argument(f"user-agent={user_agent}")
#     chrome_options.add_argument('--disable-blink-features=AutomationControlled')
#     chrome_options.add_argument("--disable-dev-shm-usage")
#     chrome_options.add_argument("--disable-notifications")
#     chrome_options.add_argument("--no-sandbox")
#     #佈署所需要的設定

#     from selenium.webdriver.chrome.service import Service
#     service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))
#     driver = webdriver.Chrome(service=service, options=chrome_options)

#     driver.get("https://www.railway.gov.tw/tra-tip-web/tip/tip001/tip121/query")

#     driver.set_window_size(1920, 1080)

#     # 填寫出發站、到達站和日期
#     driver.find_element(By.ID, "pid").send_keys(id)
#     driver.find_element(By.ID, "startStation").send_keys(startStation)
#     driver.find_element(By.ID, "endStation").send_keys(endStation)
#     driver.find_element(By.ID, "trainNoList1").send_keys(trainNoList1)
#     driver.find_element(By.ID, "rideDate1").clear()
#     driver.find_element(By.ID, "rideDate1").send_keys(rideDate1)

#     # ticketNumber = None
#     # seatNum = None
#     # orderSum = None

#     ticketNumber='6036800'
#     trainNum=trainNoList1
#     seatNum='6車20號'
#     tripTime=rideDate1
#     orderSum='255'
#     # 解決 CAPTCHA
#     from .tasks import solve_captcha_task

#     result = solve_captcha_task.delay('6LdHYnAcAAAAAI26IgbIFgC-gJr-zKcQqP1ineoz', "https://www.railway.gov.tw/tra-tip-web/tip/tip001/tip121/query")
#     # result = solve_recaptcha('6LdHYnAcAAAAAI26IgbIFgC-gJr-zKcQqP1ineoz', "https://www.railway.gov.tw/tra-tip-web/tip/tip001/tip121/query")

#     if result:
#         code = result.get(timeout=30)
#         # code = result['code']
#         # print(code)
#         # print("get recaptcha code")

#         WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "g-recaptcha-response")))
#         driver.execute_script("document.getElementById('g-recaptcha-response').innerHTML = arguments[0];", code)

#         driver.find_element(By.XPATH, "//*[@id='queryForm']/div[4]/input[2]").click()


#         # print("預定成功!以下是您的訂票資訊:\n")
#         # Select(driver.find_element(By.NAME, "orderMap['0'].ticketList[0].ticketTypeCode")).select_by_visible_text(u"全票")
#         ticketType = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.NAME, "orderMap['0'].ticketList[0].ticketTypeCode")))
#         Select(ticketType).select_by_visible_text(u"全票")

        
#         nextBtn = driver.find_element(By.CSS_SELECTOR, 'button.btn.btn-3d')
#         nextBtn.click()

#         # 等待結果加載
#         driver.implicitly_wait(5)

#        # 獲取訂票資訊
#         ticketNumber = driver.find_element(By.CLASS_NAME, 'font18').text
#         trainNum = driver.find_element(By.CLASS_NAME, 'train-trips').text
#         seatNum = driver.find_element(By.CLASS_NAME, 'seat').text
#         tripTime = driver.find_element(By.CLASS_NAME, 'time-course').text
#         orderSum = driver.find_element(By.CLASS_NAME, 'orderSum').text

#         payBtn = driver.find_element(By.XPATH, "//button[@title='下一步：付款/取票資訊']")
#         payBtn.click()
#         driver.quit() # 關閉瀏覽器

#     else:
#         print("CAPTCHA 解決失敗，請重試。")
#     driver.quit() # 關閉瀏覽器

#     # # 模擬點擊查詢按鈕
#     # orderBtn = driver.find_element(By.CSS_SELECTOR, 'input.btn.btn-3d')
#     # orderBtn.click()

#     # Select(driver.find_element(By.NAME, "orderMap['0'].ticketList[0].ticketTypeCode")).select_by_visible_text(u"全票")

#     # pyautogui.scroll(-800)
#     # nextBtn = driver.find_element(By.CSS_SELECTOR, 'button.btn.btn-3d')
#     # nextBtn.click()

#     # # 等待結果加載
#     # driver.implicitly_wait(5)

#     # # 獲取訂票資訊
#     # ticketNumber = driver.find_element(By.CLASS_NAME, 'font18').text
#     # trainNum = driver.find_element(By.CLASS_NAME, 'train-trips').text
#     # seatNum = driver.find_element(By.CLASS_NAME, 'seat').text
#     # tripTime = driver.find_element(By.CLASS_NAME, 'time-course').text
#     # orderSum = driver.find_element(By.CLASS_NAME, 'orderSum').text

#     # # 關閉瀏覽器
#     # driver.quit()

#     return {
#         'ticket_number': ticketNumber,
#         'train_number': trainNum,
#         'seat_number': seatNum,
#         'trip_time': tripTime,
#         'order_sum': orderSum,
#         'passenger_name': id   # 假設這裡用身分證字號作為乘客姓名，實際應該從表單獲取乘客姓名。
#     }

# from django.http import JsonResponse
# from celery.result import AsyncResult

# def check_task_status(request, task_id):
#     result = AsyncResult(task_id)
#     if result.state == 'PENDING':
#         return JsonResponse({'status': 'PENDING'}, status=202)
#     elif result.state == 'SUCCESS':
#         return JsonResponse(result.result, status=200)
#     elif result.state == 'FAILURE':
#         return JsonResponse({'status': 'FAILURE', 'error': str(result.result)}, status=500)
#     return JsonResponse({'status': result.state}, status=200)

#將車票存入資料庫
@login_required
def order_ticket(request):

    if request.method == 'POST':
        #接收從index.html傳來的資料
        passenger_name = request.POST.get('passenger_name')
        id_number = request.POST.get('id_number')
        schedule = request.POST.get('schedule_data')

        #對schedule做資料處理

        trainNumSet = schedule.split('(')[0]
        # match = re.search(r'(?<!\()\b\d+\b(?!\))', trainNumSet)
        # train_number = match.group()
        from_station = schedule.split(',')[1]
        to_station = schedule.split(',')[2]
        departure_time = datetime.strptime(schedule.split(',')[3], '%Y-%m-%d').date()
        go_time = schedule.split(',')[4]
        arrive_time = schedule.split(',')[5]
        passenger_name = passenger_name
        passenger_ID = id_number
        order_sum=schedule.split(',')[6]

        #存成一筆ticket object資料
        ticket=TicketOrder.objects.create(user=request.user,train_number=trainNumSet,from_station=from_station, to_station=to_station,
                                          departure_time=departure_time, passenger_name=passenger_name,
                                          passenger_ID=passenger_ID, go_time=go_time, arrive_time=arrive_time, order_sum= order_sum)
        ticket.save()#要save才儲存成功

        return redirect('order_view', ticket_id=ticket.id)
    return HttpResponse("~Sorry~")  #這裡基本不會出現，但如果有任何意外狀況，可以改跳轉到index，加上錯誤訊息

#顯示訂購結果
import time
import random
import json
from django.http import JsonResponse
from django.shortcuts import render
from .models import TicketOrder

@login_required
def order_view(request, ticket_id):
    ticket = TicketOrder.objects.get(id=ticket_id)

    # 如果這是新的會話，生成一個隨機數並儲存在會話中
    if 'number_to_guess' not in request.session:
        request.session['number_to_guess'] = random.randint(1, 100)
        request.session['attempts'] = 0

    if request.method == 'POST':
        # 檢查請求的內容類型，確保處理 JSON 請求
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            guess = data.get('guess')  # 獲取猜測值

            # 確保猜測值為整數，且在範圍內
            try:
                guess = int(guess)
            except (ValueError, TypeError):
                return JsonResponse({'message': "請輸入一個有效的數字 (1-100)。"}, status=400)

            request.session['attempts'] += 1

            if not (1 <= guess <= 100):
                message = "請輸入一個有效的數字 (1-100)。"
            else:
                if guess < request.session['number_to_guess']:
                    message = "太低了！再試一次。"
                elif guess > request.session['number_to_guess']:
                    message = "太高了！再試一次。"
                else:
                    message = f"恭喜你！你猜對了！正確的數字是 {request.session['number_to_guess']}，你用了 {request.session['attempts']} 次猜測！"
                    del request.session['number_to_guess']
                    del request.session['attempts']

            return JsonResponse({'message': message})

        # 如果是訂票提交的 POST 請求
        elif 'booking_submit' in request.POST:
            booking_info = {
                'ticket_number': random.randint(1,9999999),
                'train_number': ticket.train_number,
                'seat_number': f'{random.randint(1,8)}車{random.randint(1,44)}號',
                'trip_time': f'{ticket.departure_time} {ticket.from_station} {ticket.go_time} - {ticket.to_station} {ticket.arrive_time}',
                'order_sum': ticket.order_sum,
                'passenger_name': id  # 假設以身分證字號作為乘客姓名
            }
            # 訂票處理邏輯
        #     from .tasks import bookingTRA
        #     from celery.result import AsyncResult
        #     result = bookingTRA.delay(ticket.passenger_ID, ticket.from_station, ticket.to_station, ticket.train_number, ticket.departure_time.strftime('%Y%m%d')) 
        #     task_id = result.id
        # # 等待一段時間後檢查狀態
        #     status = AsyncResult(task_id).status
        #     print(f"當前任務狀態：{status}2")          
        #     booking_info = result.get()
            ticket.ticket_number=booking_info['ticket_number']#新增 訂票代碼 進資料庫
            ticket.seat_number=booking_info['seat_number']#新增 座位號碼 進資料庫
            ticket.order_sum=booking_info['order_sum']#新增 總金額 進資料庫
            
            ticket.save
            #寄信
            time.sleep(15)
            send_mail(
                subject='您的台鐵票訂單已確認',
                message=f'感謝您的訂購！以下是您的台鐵票訂單資訊：\n\n'
                        f'訂票代碼：{ticket.ticket_number}\n'
                        # f'身分證字號：{ticket.passenger_ID}\n'
                        # f'旅客姓名：{ticket.passenger_name}\n'
                        f'搭乘車次：{ticket.train_number}\n'                        
                        # f'訂票代碼：{ticket.ticket_number}\n'
                        f'座位號碼：{ticket.seat_number}\n'
                        # f'出發站：{ticket.from_station}\n'
                        # f'到達站：{ticket.to_station}\n'
                        f'出發日期：{ticket.departure_time}\n'
                        f'乘車時間：{ticket.from_station} {ticket.go_time} - {ticket.to_station} {ticket.arrive_time}\n'
                        f'總金額：{ticket.order_sum} 元\n',
                from_email='dusum1129@gmail.com',
                recipient_list=[request.user.email],
            )
            
            return render(request, 'order_success.html', booking_info)

    return render(request, 'schedule_form.html', {'ticket': ticket})

# from celery.result import AsyncResult
# from django.http import JsonResponse

# @login_required
# def check_task_status(request, task_id):
#     task_result = AsyncResult(task_id)
#     response = {
#         'status': task_result.status,
#         'result': task_result.result if task_result.ready() else None
#     }
#     return JsonResponse(response)

# from .tasks import bookingTRA

# @login_required
# def order_view(request, ticket_id):
#     ticket = TicketOrder.objects.get(id=ticket_id)
#     if request.method == 'POST' and 'booking_submit' in request.POST:
#         # 啟動訂票任務
#         result = bookingTRA.delay(ticket.passenger_ID, ticket.from_station, ticket.to_station, ticket.train_number, ticket.departure_time.strftime('%Y%m%d'))
        
#         # 返回 task_id 給前端輪詢
#         return JsonResponse({'task_id': result.id})

    
#     return render(request, 'schedule_form.html', {'ticket': ticket})

# @login_required
# def save_booking_info(request, task_id):
#     task_result = AsyncResult(task_id)

#     if task_result.status == 'SUCCESS':
#         # 獲取訂票資訊
#         booking_info = task_result.result

#         # 從資料庫中獲取並更新訂票紀錄
#         ticket = TicketOrder.objects.get(id=request.POST.get('ticket_id'))
#         ticket.ticket_number = booking_info['ticket_number']
#         ticket.seat_number = booking_info['seat_number']
#         ticket.order_sum = booking_info['order_sum']
#         ticket.save()

#         # 發送確認郵件
#         send_mail(
#             subject='您的台鐵票訂單已確認',
#             message=f'感謝您的訂購！以下是您的台鐵票訂單資訊：\n\n'
#                     f'身分證字號：{ticket.passenger_ID}\n'
#                     f'旅客姓名：{ticket.passenger_name}\n'
#                     f'搭乘車次：{ticket.train_number}\n'
#                     f'訂票代碼：{ticket.ticket_number}\n'
#                     f'座位號碼：{ticket.seat_number}\n'
#                     f'出發站：{ticket.from_station}\n'
#                     f'到達站：{ticket.to_station}\n'
#                     f'出發日期：{ticket.departure_time}\n'
#                     f'出發時間：{ticket.go_time}\n'
#                     f'總金額：{ticket.order_sum}\n',
#             from_email='dusum1129@gmail.com',
#             recipient_list=[request.user.email],
#         )

#         return JsonResponse({'status': 'success', 'booking_info': booking_info})
#     else:
#         return JsonResponse({'status': 'failed', 'message': '訂票尚未完成或失敗。'})