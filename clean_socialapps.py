import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from allauth.socialaccount.models import SocialApp

# Get all SocialApp objects
all_apps = SocialApp.objects.all()
print(f'Total SocialApp objects: {all_apps.count()}')

# Check for apps with empty provider or name
empty_provider = SocialApp.objects.filter(provider='')
empty_name = SocialApp.objects.filter(name='')

print(f'\nApps with empty provider: {empty_provider.count()}')
for app in empty_provider:
    print(f'  ID: {app.id}, Name: "{app.name}"')

print(f'\nApps with empty name: {empty_name.count()}')
for app in empty_name:
    print(f'  ID: {app.id}, Provider: "{app.provider}"')

# Delete apps with empty provider
if empty_provider.exists():
    print(f'\nDeleting {empty_provider.count()} apps with empty provider...')
    empty_provider.delete()

# Delete apps with empty name
if empty_name.exists():
    print(f'\nDeleting {empty_name.count()} apps with empty name...')
    empty_name.delete()

# Check final state
final_apps = SocialApp.objects.all()
print(f'\nFinal count: {final_apps.count()}')
for app in final_apps:
    print(f'  ID: {app.id}, Provider: "{app.provider}", Name: "{app.name}"')
