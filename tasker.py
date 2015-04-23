#! /usr/bin/env python

import heat
import logging
from circle import Circle, Orginfo
from celery import Celery

app = Celery('tasker')
cci = Circle()
org = Orginfo()

app.config_from_object('celeryconfig')


@app.task
def trigger_test_build():
    cci.trigger_build('rackspace-orchestration-templates/minecraft')


@app.task
def trigger_daily_builds(orgname, time_range=3600):
    """ spread triggers over time_range seconds """
    """ using Celery's `countdown` to delay     """
    logmessage = '{}/{} build triggering {}s from now'
    repos = [r for r in org.get_prod_repos(orgname)]
    index = 0
    for repo in repos:
        args = [orgname, repo]
        countdown = int(time_range*(float(index)/float(len(repos))))
        logging.info(logmessage.format(orgname, repo, countdown))
        trigger_single_build.apply_async(args=args, countdown=countdown)
        index += 1


@app.task
def trigger_single_build(orgname, repo):
    cci.trigger_build(orgname + '/' + repo)


@app.task
def trigger_failed_builds(orgname):
    for repo in org.get_prod_repos(orgname):
        if cci.get_latest_build_status(orgname, repo) == 'failed':
            logging.info(
                'failed status for ' +
                '{}/{}: triggering build'.format(orgname, repo))
            cci.trigger_build('/'.join([orgname, repo]))
        else:
            logging.info('skipping non-failing build for {}'.format(repo))
            pass


@app.task
def delete_stacks_older_than(interval, region_list):
    heat.delete_stacks_older_than(interval, region_list=region_list)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    trigger_daily_builds('rackspace-cookbooks')
    # trigger_failed_builds('rackspace-orchestration-templates')
    # for repo in org.get_prod_repos('rackspace-orchestration-templates'):
    #    cci.trigger_build('rackspace-orchestration-templates' + '/' + repo)
