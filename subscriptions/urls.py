from django.urls import path
from .views import subscribe2
app_name = 'subscriptions'

urlpatterns = [
    path('subscribe2/', subscribe2, name='subscribe2'),
]