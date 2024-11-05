from django.http import JsonResponse
from django.shortcuts import render
from .forms import EmailForm
from .models import Subscriber2
# Create your views here.

def subscribe2(request):
    if request.method == 'POST':
        print("收到请求：", request.POST)  # 打印 POST 数据
        form = EmailForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            print("表单错误：", form.errors)  # 打印表单错误
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    return JsonResponse({'success': False}, status=400)