# backend/config/celery.py

import os
from celery import Celery


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('SocialNetworkDjango')

# Load task modules from all registered Django app configs.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Look for tasks in all installed apps
app.autodiscover_tasks()

# Optional: For monitoring purposes
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
