import os
from celery.schedules import crontab

BROKER_URL = 'redis://redis:6379/0'

CELERY_TIMEZONE = os.environ.get('TZ', 'UTC')
CELERYBEAT_SCHEDULE = {
    'run-daily-builds': {
        'task': 'tasker.trigger_daily_builds',
        'schedule': crontab(hour=16, minute=45, day_of_week='*'),
        'args': ['rackspace-orchestration-templates']
    }
}
