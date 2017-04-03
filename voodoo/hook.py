#!/usr/bin/env python
# coding: utf-8

import os
import pkg_resources
import yaml
from datetime import datetime
from plumbum.cli.terminal import ask
from plumbum import local
from unidecode import unidecode


class Hook(object):

    def __init__(self, voodoo, logger):
        self.logger = logger
        self.voodoo = voodoo
        self._run = voodoo._run
        self._compose = getattr(voodoo, 'compose', None)
        super(Hook, self).__init__()


class GetMainService(Hook):
    _service = None

    def run(self):
        pass


class Deploy(Hook):
    _service = None

    def __init__(self, *args, **kwargs):
        super(Deploy, self).__init__(*args, **kwargs)
        self._called_log = []

    def _build(self):
        self._run(self._compose['build'])

    def _stop_container(self):
        self._run(self._compose['down'])

    def _start_maintenance(self):
        pass

    def _update_application(self):
        pass

    def _stop_maintenance(self):
        pass

    def _start_container(self):
        self._run(self._compose['up', '-d'])

    def _call_and_log(self, func, message):
        start = datetime.now()
        self.logger.info(message)
        getattr(self, func)()
        end = datetime.now()
        funcname = func.replace('_', ' ').strip().capitalize()
        message = '%s done in %s' % (funcname, end - start)
        self.logger.info(message)
        self._called_log.append(message)

    def _resume_log(self):
        self.logger.info("\n\nDeploy Log Resume:\n")
        for msg in self._called_log:
            self.logger.info(msg)

    def _deploy(self):
        self._call_and_log('_build', 'Start Building the application:')
        self._call_and_log('_stop_container', 'Stop the application:')
        self._call_and_log('_update_application', 'Update the application:')
        self._call_and_log('_stop_maintenance', 'Stop the maintenance page:')
        self._call_and_log('_start_container', 'Start the application:')

    def run(self):
        self._call_and_log('_deploy', 'Deploying the Application')
        self._resume_log()


class InitRunDev(Hook):
    _service = None

    def run(self):
        pass


class GenerateDevComposeFile(Hook):
    _service = None
    _map_user_for_service = None

    def __init__(self, *args, **kwargs):
        super(GenerateDevComposeFile, self).__init__(*args, **kwargs)
        # Do not use os.path.join()
        resource_path = '/%s/docker-compose.yml' % self._service
        template = pkg_resources.resource_stream(__name__, resource_path)
        self.config = yaml.safe_load(template)

    def _add_map_uid(self):
        if not self._map_user_for_service:
            return
        # inject uid for sharing file with some host
        uid = os.getuid()
        for service_name in self._map_user_for_service:
            if service_name in self.config['services']:
                service = self.config['services'][self._service]
                if not 'environment' in service:
                    service['environment'] = []
                for key in ['USERMAP_UID', 'USERMAP_GID']:
                    service['environment'].append("%s=%s" % (key,uid))

    def get_default_volume(self):
        return []

    def _add_default_volume(self):
        service = self.config['services'][self._service]
        default_volume = self.get_default_volume()
        if default_volume:
            if not 'volumes' in service:
                service['volumes'] = []
            service['volumes'] += default_volume

    def _ask_optional_service(self):
        """Container can be set as optional by adding the key
        "optional" and "description". This method will ask the user to
        use or not this optional container"""
        answer = {}
        for name, config in self.config['services'].items():
            if config.get('optional'):
                option = config['optional']
                if not option in answer:
                    answer[option] = ask(
                        "%s. Do you want to install it"
                        % option, default=False)
                if answer[option]:
                    # remove useless dockercompose key
                    del self.config['services'][name]['optional']
                    if not 'links' in self.config['services'][self._service]:
                        self.config['services'][self._service]['links'] = []
                    self.config['services'][self._service]['links'].append(name)
                else:
                    del self.config['services'][name]

    def _add_container_name(self):
        project_name = unidecode(local.cwd.name.decode('utf-8'))\
            .replace(' ', '').lower()
        for name, config in self.config['services'].items():
            expose = config.pop('expose', False)
            if expose:
                if name != self._service:
                    dns = "%s.%s.vd" %(name, project_name)
                else:
                    dns = "%s.vd" % project_name
                if not 'environment' in config:
                    config['environment'] = []
                config['environment'].append("VIRTUAL_HOST=%s" % dns)
                config['environment'].append("VIRTUAL_PORT=%s" % expose)

    def _update_config_file(self):
        self._ask_optional_service()
        self._add_map_uid()
        self._add_default_volume()
        self._add_container_name()

    def run(self):
        with open('dev.docker-compose.yml', 'w') as dc_tmp_file:
            self._update_config_file()
            dc_tmp_file.write(yaml.dump(self.config, default_flow_style=False))
