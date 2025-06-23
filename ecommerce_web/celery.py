from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery import shared_task
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce_web.settings')

app = Celery('ecommerce_web')
app.conf.enable_utc = False

app.conf.update(timezone='Asia/Kolkata')

app.config_from_object(settings, namespace='CELERY')

app.conf.beat_schedule = {
    
}

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    for i in range(11):
        print("i======================",i)
    print(f'Request: {self.request!r}')

@shared_task(bind=True)
def task_fun():
    print("=======================")    