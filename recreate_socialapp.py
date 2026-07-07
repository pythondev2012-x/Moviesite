import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

# Delete all existing SocialApps
print('Deleting all existing SocialApps...')
count = SocialApp.objects.all().delete()[0]
print(f'Deleted {count} SocialApp(s)')


# Get the current site
site = Site.objects.get_current()
print(f'Current site: {site.domain} (ID: {site.id})')

# Create new Google SocialApp
print('\nCreating new Google SocialApp...')
app = SocialApp.objects.create(
    provider='google',
    name='Google',
    client_id=settings.GOOGLE_SOCIAL_APP_CLIENT_ID,
    secret=settings.GOOGLE_SOCIAL_APP_SECRET,
    key=''
)

# Add the site to the app
app.sites.add(site)
app.save()

print(f'Created SocialApp: ID={app.id}, Name="{app.name}", Provider="{app.provider}"')
print(f'Associated with site: {site.domain}')

# Verify
print('\nVerification:')
apps = SocialApp.objects.filter(provider='google')
print(f'Total Google apps: {apps.count()}')
for app in apps:
    print(f'  ID: {app.id}, Name: "{app.name}", Sites: {[s.domain for s in app.sites.all()]}')
