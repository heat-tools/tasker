#! /usr/bin/env python

import os
import json
import logging
import requests
from circleclient import circleclient
from github import Github
from github.GithubException import UnknownObjectException, GithubException


class Circle:
    def __init__(self, circle_token=None):
        if circle_token:
            self.circle_token = circle_token
        elif os.environ.get('CCI_TOKEN', None):
            self.circle_token = os.environ['CCI_TOKEN']

        assert self.circle_token, ('You must supply a CircleCI token '
                                   'in the environment variable CCI_TOKEN or '
                                   'via command line.')

        self.cci = circleclient.CircleClient(self.circle_token)

    def get_latest_build_status(self, org_name, repo):
        """Return the most recent build status for the repo"""
        """which is a string as returned in the 'outcome' field"""
        """of the CircleCI build status document"""
        c = self.cci
        logging.info('fetching build status for {}/{}'.format(org_name, repo))
        builds = c.build.recent(org_name, repo)
        builds.sort(key=lambda build: int(build.get('build_num')))
        latest_build = builds.pop()
        logging.info(
            'latest build_num is {}'.format(latest_build.get('build_num')))
        return latest_build.get('outcome')

    def trigger_build(self, projects, gitref='master'):
        token = self.circle_token
        template = ('https://circleci.com/api/v1/project/{}'
                    '/tree/{}?circle-token={}')
        if type(projects).__name__ == 'str' or \
           type(projects).__name__ == 'unicode':
            projects = [projects]

        for project in projects:
            trigger_url = template.format(project, gitref, token)
            logging.info('triggering build for {} ref {}'.format(project, ref))
            requests.post(trigger_url)

        return True


class Orginfo:
    def __init__(self, github_token=None):
        if github_token:
            self.github_token = github_token
        elif os.environ.get('GITHUB_TOKEN', None):
            self.github_token = os.environ['GITHUB_TOKEN']
        self.gh_instance = Github(self.github_token)

    def _get_org_repos(self, org_name):
        g = self.gh_instance
        org = g.get_organization(org_name)
        return org.get_repos()

    def get_org_repos(self, org_name):
        repos = self._get_org_repos(org_name)
        return [repo.name for repo in repos]

    def get_prod_repos(self, org_name):
        g = self.gh_instance
        repos = self._get_org_repos(org_name)
        for repo in repos:
            try:
                # skip repos with no 'circle.yml' file
                if repo.get_contents('circle.yml'):
                    yield repo.name
            except (UnknownObjectException, GithubException):
                # no 'circle.yml', no don't return this one
                pass
