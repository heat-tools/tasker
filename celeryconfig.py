import os
from celery.schedules import crontab

BROKER_URL = 'redis://redis:6379/0'

CELERY_TIMEZONE = os.environ.get('TZ', 'America/Chicago')
CELERYBEAT_SCHEDULE = {
    'run-daily-builds-heat': {
        'task': 'tasker.trigger_daily_builds',
        'schedule': crontab(hour=4, minute=13),
        'args': ['rackspace-orchestration-templates']
    },
    'rebuild-failures': {
        'task': 'tasker.trigger_failed_builds',
        'schedule': crontab(hour='6,7', minute=13),
        'args': ['rackspace-orchestration-templates']
    },
    'run-daily-builds-rackspace-cookbooks': {
        'task': 'tasker.trigger_daily_builds',
        'schedule': crontab(hour=0, minute=18),
        'args': ['rackspace-cookbooks']
    },
    'run-daily-builds-AutomationSupport': {
        'task': 'tasker.trigger_daily_builds',
        'schedule': crontab(hour=0, minute=30),
        'args': ['AutomationSupport']
    }
}
