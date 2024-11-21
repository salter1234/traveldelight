from django import template
from datetime import datetime
import math
from members.models import Rating
from django.db.models import Q

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    return field.as_widget(attrs={'class': css_class})

#評論star
@register.filter(name='range_filter')
def range_filter(value):
    return range(1, value+1)

@register.filter(name='remaining_range')
def remaining_range(value):
    remaining_value = 5 - value
    return range(remaining_value)

#會員折扣(旅遊行程)
@register.filter(name='discount')
def discount(value):
    discount = int(value)-math.ceil(int(value)*0.05)
    return discount

#日期星期
@register.filter(name='weekday')
def weekday(value):
    weekday = datetime.strptime(value,"%Y-%m-%d").date()
    return weekday

#顯示每個行程的評分數量
@register.filter(name='rating5') #5星評分
def rating5(valu):
    rating = Rating.objects.filter(Q(tour=valu)&Q(value=5)).count()
    return rating
@register.filter(name='rating4') #4星評分
def rating4(valu):
    rating = Rating.objects.filter(Q(tour=valu)&Q(value=4)).count()
    return rating
@register.filter(name='rating3') #3星評分
def rating3(valu):
    rating = Rating.objects.filter(Q(tour=valu)&Q(value=3)).count()
    return rating
@register.filter(name='rating2') #2星評分
def rating2(valu):
    rating = Rating.objects.filter(Q(tour=valu)&Q(value=2)).count()
    return rating
@register.filter(name='rating1') #1星評分
def rating1(valu):
    rating = Rating.objects.filter(Q(tour=valu)&Q(value=1)).count()
    return rating

@register.filter(name='rating') #1星評分
def rating(valu):
    num = Rating.objects.filter(Q(tour=valu)).count()
    if num==0:
        return True
    else:
        return False

#辨別車種
@register.filter(name='traintype')
def traintype(value):
    value=value.split(" ")[0]
    if "自強" in value:
        return True
    else:
        return False

#日曆顯示(已過期)    
@register.filter(name='comparedate')
def comparedate(go):
    go=datetime.strptime(go,"%Y-%m-%d").date()
    date=datetime.today().date()
    if go <= date:
        return True
    else:
        return False

#日曆顯示(已滿團) 
@register.filter(name='compare')
def compare(go, earligodate):
    go=datetime.strptime(go,"%Y-%m-%d").date()
    earligodate=datetime.strptime(earligodate.replace('/', '-').strip(),"%Y-%m-%d").date()
    if go < earligodate:
        return True
    else:
        return False
    
#order不顯示過期日 
@register.filter(name='now')
def now(value):
    today=datetime.today().date()
    godate=datetime.strptime(value.replace('/', '-').strip(),"%Y-%m-%d").date()
    if godate <= today:
        return True
    else:
        return False