import os

from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sitewomen.settings')
app = Celery('sitewomen', broker_connection_retry=False,
             broker_connection_retry_on_startup=True, )
app.config_from_object('django.conf:settings')

app.autodiscover_tasks()
app.conf.beat_schedule = {
    'send-report-every-single-minute': {
        'task': 'women.tasks.send_view_count_report',
        'schedule': crontab(minute=0, hour=23),
    },
    'delete-old-posts': {
        'task': 'women.tasks.delete_old_posts',
        'schedule': crontab(minute=59, hour=23),
    }
}