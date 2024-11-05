from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import date

from django.utils import timezone

class MemberManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('用户必须有一个邮箱地址')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

class Member(AbstractBaseUser, PermissionsMixin):
    date_joined = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)  # 额外字段
    location = models.CharField(max_length=30, blank=True)  # 额外字段
    birth_date = models.DateField(null=True, blank=True)  # 额外字段
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    line_id = models.CharField(max_length=100, null=True, blank=True)  # 新增的 Line ID 欄位
    question_count = models.PositiveIntegerField(default=0)  # 記錄今日提問數量
    last_question_date = models.DateField(null=True, blank=True)  # 記錄提問日期


    objects = MemberManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    # 使用related_name区分不同模型之间的groups和user_permissions字段
    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='member_set',  # 改变related_name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', 
        related_name='member_set',  # 改变related_name
        blank=True
    )

class MemberProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def delete(self, *args, **kwargs):
        # 删除头像文件
        if self.avatar:
            self.avatar.delete(save=False)  # 只删除文件，不保存模型
        super().delete(*args, **kwargs)  # 删除模型实例

# 如果您需要 CustomUser ，可以将其定义如下：
class CustomUser(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', default='avatars/image.png')

    # 同样使用related_name区分
    groups = models.ManyToManyField(
        'auth.Group', 
        related_name='customuser_set',  # 改变related_name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', 
        related_name='customuser_set',  # 改变related_name
        blank=True
    )

from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.name


from social_core.exceptions import SocialAuthBaseException
from .models import Member
from social_core.exceptions import SocialAuthBaseException

def create_user(backend, uid, user=None, response=None, *args, **kwargs):
    email = response.get('email')

    # 如果用户已存在，直接返回
    if user is not None:
        return {
            'is_new': False,
            'user': user,
        }

    # 尝试根据电子邮件查找用户
    try:
        user = Member.objects.get(email=email)
        # 如果用户存在，则返回该用户
        return {
            'is_new': False,
            'user': user,
        }
    except Member.DoesNotExist:
        # 如果用户不存在，则创建新用户
        user = Member(email=email, username=email)
        user.set_unusable_password()  # 不希望用户有密码
        user.save()  # 确保只有在没有相同电子邮件的情况下才能保存
        return {
            'is_new': True,
            'user': user,
        }

class CustomUserModelBackend:
    def create_user(self, *args, **kwargs):
        email = kwargs.get('email')

        # 检查电子邮件是否已存在
        if email and Member.objects.filter(email=email).exists():
            # 如果已存在用户，更新用户信息
            existing_user = Member.objects.get(email=email)
            # 更新用户信息，比如名字、头像等
            existing_user.name = kwargs.get('name', existing_user.name)  # 假设有 name 字段
            existing_user.profile_picture = kwargs.get('avatars', existing_user.profile_picture)  # 假设有 profile_picture 字段
            existing_user.save()
            return existing_user  # 返回已存在的用户

        # 创建新用户
        try:
            user = Member.objects.create_user(*args, **kwargs)  # 适当传递参数以创建用户
            return user
        except Exception as e:
            raise SocialAuthBaseException(f"Failed to create user: {e}")



"""
by 芷翎(新增旅遊行程、區域、景點、目的地、旅行社model)
"""
# 定義區域
class Region(models.Model):
    region_name = models.CharField(max_length=100, unique=True)  # 區域名稱，如"北部"
    
    def __str__(self):
        return self.region_name

# 定義城市模型，並與區域建立外鍵關係
class Site(models.Model):
    site_name = models.CharField(max_length=100, unique=True)  # 城市名稱，如"台北"
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='sites')  # 將城市與區域關聯

    def __str__(self):
        return f'{self.site_name}'

#旅行社
class Company(models.Model):
    company_name = models.CharField(max_length=150, blank=False)
    def __str__(self):
        return self.company_name

#景點
class Attraction(models.Model):
    attraction_name = models.CharField(max_length=150)
    def __str__(self):
        return self.attraction_name

# 旅遊行程
class Tour(models.Model):
    NormGroupID = models.CharField(max_length=150, null=True) #爬蟲時決定是否新增資料的比對號碼
    tourname = models.CharField(max_length=300, null=True) #旅遊標題名稱
    toursite = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='tours_as_toursite', null=True) #旅遊目的地
    company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=False) #旅行社
    tourlink = models.CharField(max_length=300, null=True) # 旅遊行程連結
    gosite = models.ManyToManyField(Site, through="TourSite", through_fields=('tour', 'site'), related_name='tours_as_gosite')# 出發城市
    tourimage = models.CharField(max_length=300, null=True) # 旅遊行程圖片
    tourday = models.PositiveIntegerField(default=1, blank=False) # 旅遊天數
    price = models.DecimalField(max_digits=8, decimal_places=0, null=False) # 費用   
    earlierGoDate = models.CharField(max_length=200, null=True)     # 最早可出發日期
    create_date = models.DateField(default=timezone.now, null=False)  #建立行程時間
    renew_date = models.DateTimeField(default=timezone.now, null=False)  #更新可出發日期時間
    tourSpecial = models.CharField(max_length=2000, blank=True, default='') #旅遊行程特色描述
    goDate = models.CharField(max_length=2000, null=True)#旅遊出團日期
    attraction=models.ManyToManyField(Attraction, through="TourAttraction", through_fields=('tour', 'attraction'), related_name='tours_as_attraction')
    day = models.CharField(max_length=50, null=True) #旅遊天數
    travelPoint = models.CharField(max_length=2000, null=True) #旅遊景點
    breakfast = models.CharField(max_length=100, null=True) #早餐
    lunch = models.CharField(max_length=100, null=True) #午餐
    dinner = models.CharField(max_length=100, null=True) #晚餐
    hotel = models.CharField(max_length=200, null=True) #住宿

    #機器學習資料
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)  # 用戶評分
    view_count = models.PositiveIntegerField(default=0)  # 瀏覽次數
    category = models.CharField(max_length=100, null=True, blank=True)  # 旅遊類別
    tags = models.CharField(max_length=255, null=True, blank=True)  # 旅遊標籤
    region = models.CharField(max_length=100, null=True)  # 行程所屬地區
    season = models.CharField(max_length=50, null=True)  # 推薦適合的季節
    def __str__(self):
        return f'{self.toursite} - {self.tourname}'
    
class TourSite(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='toursites_as_tour')
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    
    
class TourAttraction(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='tourattractions_as_tour')
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE)

"""
by 正融(新增評論model)
"""
# 評分的表
class Rating(models.Model):
    # 加外鍵從 member 獲取資料
    user_name = models.ForeignKey(Member, on_delete=models.CASCADE, blank=False)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, blank=False) #旅遊行程 
    value = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Rating: {self.value}'
    
    
"""
by 奕誠(新增我的最愛行程)
"""
from django.contrib.auth import get_user_model
User = get_user_model()
#我的最愛    
class FavoriteTrip(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, blank=False) #旅遊行程 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s favorite trip: {self.tour.tourname}"
    
class Subscriber(models.Model):
    email = models.EmailField(max_length=254, unique=True)

    def __str__(self):
        return self.email

#機器學習存取用戶操作
class UserBehavior(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=20)  # 例如 'view', 'favorite', 'order'
    timestamp = models.DateTimeField(auto_now_add=True)

from django.db import models
from django.contrib.auth.models import User


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

"""
by 齡文(車票&訂單)
"""
#車票訂單
# class TicketOrder(models.Model):

#     train_number = models.CharField(max_length=100, default='Unknown')#搭乘車次
#     from_station = models.CharField(max_length=100)#出發地
#     to_station = models.CharField(max_length=100)#抵達地
#     departure_time = models.DateField()#出發日期
#     passenger_name = models.CharField(max_length=100)#旅客姓名(會許可以foriegnKey會員資料)
#     passenger_ID = models.CharField(max_length=30,default=False)#旅客身分證字號
#     go_time = models.CharField(max_length=30,default=False)#出發時間
#     order_time = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Order for {self.passenger_name} on {self.from_station} to {self.to_station} at {self.departure_time}"

#旅遊行程訂單
class TourOrder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    gosite = models.CharField(max_length=10)
    godate = models.DateField()
    status = models.CharField(max_length=10, default='Pending')
    order_sum = models.CharField(max_length=30,null=True)#總金額
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.tour.tourname}-{self.gosite}-{self.godate}'



#車票訂單
class TicketOrder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    train_number = models.CharField(max_length=100, default='Unknown')#搭乘車次
    from_station = models.CharField(max_length=100)#出發地
    to_station = models.CharField(max_length=100)#抵達地
    departure_time = models.DateField()#出發日期
    passenger_name = models.CharField(max_length=100)#旅客姓名(會許可以foriegnKey會員資料)
    passenger_ID = models.CharField(max_length=30,default=False)#旅客身分證字號
    go_time = models.CharField(max_length=30,default=False)#出發時間
    arrive_time = models.CharField(max_length=30,default=False)#出發時間
    order_time = models.DateTimeField(auto_now_add=True)
    ticket_number = models.CharField(max_length=30,null=True)#訂票代碼
    seat_number = models.CharField(max_length=30,null=True)#座位號碼
    order_sum = models.CharField(max_length=30,null=True)#總金額

    def __str__(self):
        return f"Order for {self.passenger_name} on {self.from_station} to {self.to_station} at {self.departure_time}"