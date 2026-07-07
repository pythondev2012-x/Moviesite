from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Agar user allaqachon mavjud bo'lsa, hech narsa qilmaymiz
        if sociallogin.user.pk:
            return
        
        # Email orqali user borligini tekshiramiz
        email = sociallogin.account.extra_data.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
                # Agar user bor bo'lsa, sociallogin'ni shu userga bog'laymiz
                sociallogin.user = user
            except User.DoesNotExist:
                pass
