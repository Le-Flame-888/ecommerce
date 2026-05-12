from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # List of admin emails or domains allowed to be staff
        admin_emails = [
            'admin@luxeshop.com',
            # 'your-personal-email@gmail.com',
        ]
        
        email = sociallogin.user.email
        if email in admin_emails or email.endswith('@luxeshop.com'):
            sociallogin.user.is_staff = True
            # sociallogin.user.is_superuser = True # Uncomment if you want full admin
