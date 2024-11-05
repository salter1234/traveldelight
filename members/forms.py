#%%奕誠
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Member, Site, Company  # 确保你的 Member 模型在 models.py 中定义
from django.forms import FileInput  # 导入 FileInput
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .models import Subscriber

User = get_user_model()

# 注册表单
class MemberSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)  # 确保 email 字段是必填的

    class Meta:
        model = Member  # 使用自定义的 Member 模型
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

# 用户资料表单
class MemberProfileForm(forms.ModelForm):
    class Meta:
        model = Member  # 使用自定义的 Member 模型
        fields = ['username', 'email', 'avatar']  # 包含 avatar 字段，并允许用户编辑
        widgets = {
            'avatar': FileInput(),  # 使用 FileInput 而不是 ClearableFileInput，去除“清除”选项
        }
        labels = {
            'avatar': '頭像',  # 修改头像字段的标签
        }
        help_texts = {
            'avatar': '勾選以刪除當前頭像',  # 修改提示文本为繁体字
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['username', 'email', 'password']  # 根据需要添加字段

#搜尋旅遊行程表單
class DateWhereForm(forms.Form):
    #出發日期欄位
    firstDate = forms.DateField(widget=forms.DateInput(attrs={'class' : 'form-control', 'type':'date', 'id':"firstDate", 
                                                              'value':datetime.today().date(),'min':datetime.today().date()}), required=True)

    #回程日期欄位
    lastDate = forms.DateField(widget=forms.DateInput(attrs={'class' : 'form-control', 'type':'date', 
                                                             'value':datetime.today().date()-relativedelta(months=-2)}), 
                                                             required=False)
    #增加屬性或條件用
    lastDate.widget.attrs.update({'min':datetime.today().date(), 'max':datetime.today().date()-relativedelta(months=-3)})
    
    #目的地欄位
    seleSite = forms.ModelChoiceField(queryset=Site.objects.all(), empty_label="目的地", required=False)
    #增加屬性或條件用
    seleSite.widget.attrs.update({'class':"form-select", 'id':"seleSite"})
    
    
    #旅遊天數欄位
    day = forms.MultipleChoiceField(
        required=True,
        label='旅遊天數',
        choices=((1,'1天'),(2,'2天'),(3,'3天'),(4,'4天以上')),        
        widget=forms.widgets.CheckboxSelectMultiple(attrs={'class':"form-check-input"})
    )
    #旅遊公司欄位
    comp = forms.ModelMultipleChoiceField(queryset=Company.objects.all(),
        required=True,
        label='旅遊公司',
        widget=forms.widgets.CheckboxSelectMultiple(attrs={'class':"form-check-input"})
    )
    #依最早出發日期or價位排序欄位
    option = forms.ChoiceField(required=True, widget=forms.RadioSelect(
    attrs={'autocomplete':"off"}), choices=(('P','依照價格排序'),('E','依照最早出發日期排序')),label=False,)


"""
by 正融(使用者評論)
"""
# 評分的表單處理
class RatingForm(forms.Form):
    value = forms.IntegerField(min_value=1, max_value=5)
    comment = forms.CharField(required=False, widget=forms.Textarea)

class EmailForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your E-mail Address'})
        }