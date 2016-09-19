#!/usr/bin/env python
# coding: utf-8

import os
import pkg_resources
import yaml

class Hook(object):

    def __init__(self, voodoo):
        self._run = voodoo._run
        self._compose = getattr(voodoo, 'compose', None)
        self.env = voodoo.parent.env
        super(Hook, self).__init__()


class Deploy(Hook):
    _service = None

    def _build(self):
        self._run(self._compose['build'])

    def _stop_container(self):
        self._run(self._compose['down'])

    def _start_maintenance(self):
        pass

    def _update_app(self):
        pass

    def _stop_maintenance(self):
        pass

    def _start_container(self):
        self._run(self._compose['up', '-d'])

    def run(self):
        print '== Start Building the application =='
        self._build()
        print '== Stop the application =='
        self._stop_container()
        print '== Start the maintenance page =='
        self._start_maintenance()
        print '== Update the application =='
        self._update_app()
        print '== Stop the maintenance page =='
        self._stop_maintenance()
        print '== Start the application =='
        self._start_container()


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

    def _add_shared_home(self):
        # share .voodoo folder in voodoo
        home = os.path.expanduser("~")
        shared = os.path.join(home, '.voodoo', 'shared')
        service = self.config['services'][self._service]
        if not 'volumes' in service:
            service['volumes'] = []
        service['volumes'].append('%s:%s' % (shared, shared))

    def _update_config_file(self):
        self._add_shared_home()
        self._add_map_uid()

    def run(self):
        with open('dev.docker-compose.yml', 'w') as dc_tmp_file:
            self._update_config_file()
            dc_tmp_file.write(yaml.dump(self.config, default_flow_style=False))
