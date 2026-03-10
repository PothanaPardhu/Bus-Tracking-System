from django.test import Client
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','qrcodeproject.settings')
import django
django.setup()
client=Client()
resp=client.get('/api/v1/tracking/buses/?bus_class=1')
print('status', resp.status_code)
try:
    data=resp.json()
    print('type:', type(data))
    if isinstance(data, dict):
        print('keys:', list(data.keys()))
        if 'results' in data:
            print('results count', len(data['results']))
    elif isinstance(data, list):
        print('list len', len(data))
    else:
        print('data preview', data)
except Exception as e:
    print('no json', e)
