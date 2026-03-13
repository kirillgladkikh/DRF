import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

# Конфигурация Celery Beat
app.conf.beat_schedule = {
    'block-inactive-users-daily': {
        'task': 'users.tasks.block_inactive_users',
        'schedule': crontab(hour=2, minute=0),  # Ежедневно в 02:00
    },
}

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
