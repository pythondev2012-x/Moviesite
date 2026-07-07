import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.db import connection

# Check using raw SQL
with connection.cursor() as cursor:
    cursor.execute('SELECT id, provider, name, client_id FROM socialaccount_socialapp')
    rows = cursor.fetchall()
    print(f'Raw SQL - Total rows: {len(rows)}')
    for row in rows:
        print(f'  ID: {row[0]}, Provider: "{row[1]}", Name: "{row[2]}", Client ID: {row[3]}')

print('\n' + '='*50 + '\n')

# Check using ORM
apps = SocialApp.objects.all()
print(f'ORM - Total: {apps.count()}')
for app in apps:
    print(f'  ID: {app.id}, Provider: "{app.provider}", Name: "{app.name}", Client ID: {app.client_id}')
    print(f'    Sites: {[s.domain for s in app.sites.all()]}')
