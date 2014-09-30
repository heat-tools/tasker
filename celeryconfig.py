import os
from celery.schedules import crontab

BROKER_URL = 'redis://redis:6379/0'

CELERY_TIMEZONE = os.environ.get('TZ', 'UTC')
CELERYBEAT_SCHEDULE = {
    'run-daily-builds': {
        'task': 'tasker.trigger_daily_builds',
        'schedule': crontab(hour=9, minute=13),
        'args': ['rackspace-orchestration-templates']
    },
    'rebuild-failures': {
        'task': 'tasker.trigger_failed_builds',
        'schedule': crontab(hour=11, minute=13),
        'args': ['rackspace-orchestration-templates']
    }
}
