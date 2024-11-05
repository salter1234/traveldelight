from django.contrib import admin
from django.contrib import messages
from .models import Member  # 确保从你的 members 应用中导入 Member 模型
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import TicketOrder


admin.site.register(TicketOrder)
# 自定义 MemberAdmin 类
class CustomMemberAdmin(UserAdmin):
    # 显示的字段
    list_display = ('username', 'email', 'is_active', 'is_staff')
    readonly_fields = ['date_joined', 'last_login']  # 确保这些字段是只读的
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),  # 放在只读字段中
    )
    

    def delete_members(self, request, queryset):
        count = queryset.count()
        queryset.delete()  # 删除选定的用户
        messages.success(request, f'已成功删除 {count} 个会员')

    delete_members.short_description = "删除选定的会员"  # 操作描述

# 注册自定义 Admin 类
admin.site.register(Member, CustomMemberAdmin)  # 注册自定义的 MemberAdmin

# from .models import Comment  # 导入评论模型
# 管理評論功能
# @admin.register(Comment)
# class CommentAdmin(admin.ModelAdmin):
#     list_display = ('user', 'tour', 'content', 'created_at', 'is_active')  # 显示的字段
#     search_fields = ('content',)  # 可搜索的字段
#     list_filter = ('is_active',)  # 可过滤的字段

#     def get_queryset(self, request):
#         queryset = super().get_queryset(request)
#         return queryset.select_related('user', 'tour')  # 优化查询

# #添加自定义操作，批量删除评论或更改评论状态
# def activate_comments(modeladmin, request, queryset):
#     queryset.update(is_active=True)

# activate_comments.short_description = "Activate selected comments"

# def deactivate_comments(modeladmin, request, queryset):
#     queryset.update(is_active=False)

# deactivate_comments.short_description = "Deactivate selected comments"

# @admin.register(Comment)
# class CommentAdmin(admin.ModelAdmin):
#     actions = [activate_comments, deactivate_comments]
