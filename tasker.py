#! /usr/bin/env python

import logging
import os
from datetime import timedelta
from circle import Circle, Orginfo
from github import Github
from celery import Celery
from celery.schedules import crontab

app = Celery('tasker')
cci = Circle()
org = Orginfo()

app.config_from_object('celeryconfig')


@app.task
def trigger_test_build():
    cci.trigger_build('rackspace-orchestration-templates/minecraft')


@app.task
def trigger_daily_builds(orgname):
    for repo in org.get_prod_repos(orgname):
        cci.trigger_build('rackspace-orchestration-templates' + '/' + repo)


@app.task
def trigger_failed_builds(orgname):
    for repo in org.get_prod_repos(orgname):
        if cci.get_latest_build_status(orgname, repo) == 'failed':
            logging.info('failed status for {}/{}: triggering build'.format(orgname, repo))
            cci.trigger_build('/'.join([orgname, repo]))
        else:
            logging.info('skipping non-failing build for {}'.format(repo))
            pass

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    trigger_daily_builds('rackspace-orchestration-templates')
    # trigger_failed_builds('rackspace-orchestration-templates')
    # for repo in org.get_prod_repos('rackspace-orchestration-templates'):
    #    cci.trigger_build('rackspace-orchestration-templates' + '/' + repo)
