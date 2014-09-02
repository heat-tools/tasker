#! /usr/bin/env python

import json
import requests
import celery


class circle:
    def __init__(self, circle_token):
        self.circle_token = circle_token

    def trigger_build(project, gitref):
        template = ('https://circleci.com/api/v1/project/{}'
                    '/tree/{}?circle-token={}')
        trigger_url = template.format(project, gitref, self.circle_token)
        r = requests.post(trigger_url)
        return json.loads(r.content)
