from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elearning_platform.settings')

app = Celery('webapp')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(['webapp'])

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
