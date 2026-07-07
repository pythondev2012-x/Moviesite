import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from allauth.socialaccount.models import SocialApp
from django.db import connection

# Check for apps with empty client_id
with connection.cursor() as cursor:
    cursor.execute('SELECT id, provider, name, client_id FROM socialaccount_socialapp WHERE client_id IS NULL OR client_id = ""')
    rows = cursor.fetchall()
    print(f'Apps with empty client_id: {len(rows)}')
    for row in rows:
        print(f'  ID: {row[0]}, Provider: "{row[1]}", Name: "{row[2]}", Client ID: {row[3]}')

print('\n' + '='*50 + '\n')

# Check for apps with empty name
with connection.cursor() as cursor:
    cursor.execute('SELECT id, provider, name, client_id FROM socialaccount_socialapp WHERE name IS NULL OR name = ""')
    rows = cursor.fetchall()
    print(f'Apps with empty name: {len(rows)}')
    for row in rows:
        print(f'  ID: {row[0]}, Provider: "{row[1]}", Name: "{row[2]}", Client ID: {row[3]}')

print('\n' + '='*50 + '\n')

# Check ALL apps
with connection.cursor() as cursor:
    cursor.execute('SELECT id, provider, name, client_id FROM socialaccount_socialapp')
    rows = cursor.fetchall()
    print(f'ALL apps: {len(rows)}')
    for row in rows:
        print(f'  ID: {row[0]}, Provider: "{row[1]}", Name: "{row[2]}", Client ID: {row[3]}')
