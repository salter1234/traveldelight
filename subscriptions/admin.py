from django.contrib import admin
from .models import Subscriber2

# Register your models here.
@admin.register(Subscriber2)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email',)
    search_fields = ('email',)