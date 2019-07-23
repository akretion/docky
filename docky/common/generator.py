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
        project_name = slugify(local.cwd.name)
        config = template.read().replace(
            b'PROJECT_NAME', project_name.encode('utf-8'))
        self.config = yaml.safe_load(config)

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

    def generate(self):
        self._ask_optional_service()
        with open('dev.docker-compose.yml', 'w') as dc_tmp_file:
            dc_tmp_file.write(yaml.dump(
                self.config, Dumper=IndentDumper, default_flow_style=False))
