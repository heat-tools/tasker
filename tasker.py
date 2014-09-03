#! /usr/bin/env python

import os
from datetime import timedelta
from circle import Circle, Orginfo
from github import Github
from celery import Celery
from celery.schedules import crontab

app = Celery('tasker', broker='redis://redis:6379/0')
cci = Circle()
org = Orginfo()

app.conf.CELERY_TIMEZONE = os.environ.get('TZ', 'UTC')
app.conf.CELERYBEAT_SCHEDULE = {
    'run-daily-builds': {
        'task': 'tasker.trigger_daily_builds',
        'schedule': crontab(hour=16, minute=30, day_of_week='wed'),
        'args': ()
    }
}


@app.task
def trigger_test_build():
    cci.trigger_build('rackspace-orchestration-templates/minecraft')


@app.task
def trigger_daily_builds(orgname):
    for repo in org.get_prod_repos(orgname):
        cci.trigger_build('rackspace-orchestration-templates' + '/' + repo)

if __name__ == '__main__':
    for repo in org.get_prod_repos('rackspace-orchestration-templates'):
        cci.trigger_build('rackspace-orchestration-templates' + '/' + repo)
