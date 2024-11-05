from django.contrib.auth import get_user_model
from social_core.exceptions import AuthException

User = get_user_model()

def associate_by_email(strategy, details, user=None, *args, **kwargs):
    # 检查用户是否已经存在，使用邮箱来判断
    email = details.get('email')
    if user:
        return
    if email:
        try:
            user = User.objects.get(email=email)
            return {'is_new': False, 'user': user}
        except User.DoesNotExist:
            return
    raise AuthException("No account with this email address.")