
import datetime
import dateutil.parser
import heatclient.v1
import logging
import os
import pytz
import keystoneclient.v2_0.client as ksclient


class OSAuth(object):

    def __init__(self, region=None):
        self.creds = self.get_keystone_creds(region=region)
        self.keystone_client = ksclient.Client(**self.creds)
        if not self.creds.get('region_name'):
            sc = self.keystone_client.service_catalog.catalog
            self.creds['region_name'] = \
                sc['user'].get('RAX-AUTH:defaultRegion')

    def get_keystone_creds(self, region=None):
        creds = {}
        creds['username'] = os.environ['OS_USERNAME']
        creds['auth_url'] = os.environ['OS_AUTH_URL']
        creds['tenant_id'] = os.environ['OS_TENANT_ID']
        if region:
            creds['region_name'] = region
        else:
            creds['region_name'] = os.environ.get('OS_REGION_NAME')
        if creds.get('region_name'):
            creds['region_name'] = creds['region_name'].upper()
        if os.environ.get('OS_AUTH_TOKEN'):
            creds['token'] = os.environ['OS_AUTH_TOKEN']
        else:
            creds['password'] = os.environ['OS_PASSWORD']
        return creds

    def get_token(self):
        return self.keystone_client.auth_token

    def get_heat_url(self):
        if os.environ.get('HEAT_URL'):
            return os.environ.get('HEAT_URL')
        else:
            region = self.creds.get('region_name')
            heat_url = self.keystone_client.service_catalog.url_for(
                service_type='orchestration',
                endpoint_type='publicURL', region_name=region)
            return heat_url


class SimpleHeatClient(object):
    def __init__(self, region=None):
        self.os_client = OSAuth(region=region)
        self.os_token = self.os_client.get_token()
        self.heat_url = self.os_client.get_heat_url()
        self.heat_client = heatclient.v1.Client(endpoint=self.heat_url,
                                                token=self.os_token)
        self.stack_id = None

    def get_heat_url(self):
        return self.heat_url

    def list_stacks(self):
        return self.heat_client.stacks.list()

    def build_stack(self, stack_name, template, parameters={}, files={}):
        data = {"stack_name": stack_name,
                "template": template,
                "parameters": parameters,
                "files": files
                }
        self.stack_id = self.heat_client.stacks.create(**data)
        return self.stack_id

    def stack_status(self, stack_id):
        status = self.heat_client.stacks.get(stack_id)
        return status


def stacks_older_than(interval, region=None):
    now = datetime.datetime.now(pytz.UTC)
    shc = SimpleHeatClient(region=region)
    for stack in shc.list_stacks():
        creation_time = dateutil.parser.parse(stack.creation_time)
        age = now - creation_time
        if age > interval:
            logging.info(
                "Stack {} is older than {}".format(stack.stack_name, interval)
            )
            yield stack


def delete_stacks_older_than(interval, region_list=[None]):
    for region in region_list:
        logging.info("cleaning up stacks in region {}...".format(region))
        for old_stack in stacks_older_than(interval, region=region):
            logging.info(
                "deleting stack {}, id {}".format(
                    old_stack.stack_name, old_stack.id
                )
            )
            old_stack.delete()
