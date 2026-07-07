import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from allauth.socialaccount.models import SocialApp

# Get all Google apps
apps = SocialApp.objects.filter(provider='google')
print(f'Found {apps.count()} Google apps')

for app in apps:
    print(f'  - ID: {app.id}, Name: "{app.name}", Client ID: {app.client_id}')

# Delete all except the first one
if apps.count() > 1:
    first_app = apps.first()
    print(f'\nKeeping app ID: {first_app.id}')
    
    # Delete the rest
    for app in apps[1:]:
        print(f'Deleting app ID: {app.id}')
        app.delete()
    
    print(f'\nRemaining Google apps: {SocialApp.objects.filter(provider="google").count()}')
