import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from allauth.socialaccount.models import SocialApp

# Get all SocialApp objects
apps = SocialApp.objects.all()
print(f'Total SocialApp objects: {apps.count()}')

for app in apps:
    print(f'  - ID: {app.id}, Provider: "{app.provider}", Name: "{app.name}", Client ID: {app.client_id}')
