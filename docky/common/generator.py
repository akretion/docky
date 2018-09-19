#!/usr/bin/env python
# coding: utf-8

import yaml
import pkg_resources
from plumbum.cli.terminal import ask
from plumbum import local
from slugify import slugify


class IndentDumper(yaml.Dumper):

    def increase_indent(self, flow=False, indentless=False):
        return super(IndentDumper, self).increase_indent(flow, False)


class GenerateComposeFile(object):

    def __init__(self, service):
        super(GenerateComposeFile, self).__init__()
        # Do not use os.path.join()
        self.service = service
        resource_path = '../template/%s.docker-compose.yml' % service
        template = pkg_resources.resource_stream(__name__, resource_path)
        self.config = yaml.safe_load(template)

    def _ask_optional_service(self):
        """Container can be set as optional by adding the key
        "optional" and "description". This method will ask the user to
        use or not this optional container"""
        answer = {}
        for name, config in self.config['services'].copy().items():
            if config.get('optional'):
                option = config['optional']
                if not option in answer:
                    answer[option] = ask(
                        "%s. Do you want to install it"
                        % option, default=False)
                if answer[option]:
                    # remove useless docker compose key
                    del self.config['services'][name]['optional']
                    if not 'links' in self.config['services'][self.service]:
                        self.config['services'][self.service]['links'] = []
                    self.config['services'][self.service]['links'].append(name)
                else:
                    del self.config['services'][name]

    def _add_container_name(self):
        project_name = slugify(local.cwd.name)
        for name, config in self.config['services'].items():
            expose = config.pop('expose', False)
            if expose:
                if name != self.service:
                    dns = "%s.%s.dy" %(name, project_name)
                else:
                    dns = "%s.dy" % project_name
                if not 'environment' in config:
                    config['environment'] = []
                config['environment'].append("VIRTUAL_HOST=%s" % dns)
                config['environment'].append("VIRTUAL_PORT=%s" % expose)
                config['networks'] = {}
                config['networks']['default'] = {}
                config['networks']['default']['aliases'] = []
                config['networks']['default']['aliases'].append(dns)

    def _update_config_file(self):
        self._ask_optional_service()
        self._add_container_name()

    def generate(self):
        self._update_config_file()
        with open('dev.docker-compose.yml', 'w') as dc_tmp_file:
            dc_tmp_file.write(yaml.dump(
                self.config, Dumper=IndentDumper, default_flow_style=False))
