import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

# Get all SocialApp objects
apps = SocialApp.objects.all()
print(f'Total SocialApp objects: {apps.count()}')

for app in apps:
    print(f'  - ID: {app.id}, Provider: "{app.provider}", Name: "{app.name}", Client ID: {app.client_id}')
    print(f'    Sites: {list(app.sites.all())}')

# Get current site
site = Site.objects.get_current()
print(f'\nCurrent site: {site.domain} (ID: {site.id})')

# Check if there are apps with empty provider or name
empty_apps = SocialApp.objects.filter(provider='')
if empty_apps.exists():
    print(f'\nFound {empty_apps.count()} apps with empty provider')
    for app in empty_apps:
        print(f'  Deleting ID: {app.id}')
        app.delete()
