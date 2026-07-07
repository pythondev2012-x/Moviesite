import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from allauth.socialaccount.models import SocialApp

# Get all SocialApp objects
apps = SocialApp.objects.all()
print(f'Total SocialApp objects: {apps.count()}')

# Delete apps with empty name
empty_name_apps = SocialApp.objects.filter(name='')
if empty_name_apps.exists():
    print(f'\nFound {empty_name_apps.count()} apps with empty name')
    for app in empty_name_apps:
        print(f'  Deleting ID: {app.id}, Provider: "{app.provider}"')
        app.delete()

# Check again
apps = SocialApp.objects.all()
print(f'\nAfter cleanup: {apps.count()} SocialApp objects')
for app in apps:
    print(f'  - ID: {app.id}, Provider: "{app.provider}", Name: "{app.name}"')
