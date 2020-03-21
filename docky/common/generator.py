#!/usr/bin/env python
# coding: utf-8

import yaml
import pkg_resources
from plumbum.cli.terminal import ask, prompt
from plumbum.cmd import echo, id
from plumbum import local
from slugify import slugify
from compose.config.environment import Environment

from ..common.api import logger


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
        config = template.read()
        self.config = yaml.safe_load(config)

    def _ask_optional_service(self):
        """Container can be set as optional by adding the key
        "optional" and "description". This method will ask the user to
        use or not this optional container"""
        answer = {}
        for name, config in self.config['services'].copy().items():
            if config.get('optional'):
                option = config['optional']
                if option not in answer:
                    answer[option] = ask(
                        "%s. Do you want to install it"
                        % option, default=False)
                if answer[option]:
                    # remove useless docker compose key
                    del self.config['services'][name]['optional']
                    if 'links' not in self.config['services'][self.service]:
                        self.config['services'][self.service]['links'] = []
                    self.config['services'][self.service]['links'].append(name)
                else:
                    del self.config['services'][name]

    def generate(self):
        self._ask_optional_service()
        with open('docker-compose.yml', 'w') as dc_tmp_file:
            dc_tmp_file.write(yaml.dump(
                self.config, Dumper=IndentDumper, default_flow_style=False))


class GenerateEnvFile(object):
    '''Create or add some variables to .env.

    If a variable is already present, don't change it
    '''
    def _key_compose_file(self):
        # create an (prod|dev).docker-compose.yml
        # and set it in compose_file variable
        # TODO: extract it
        # TODO: create file properly
        env_file = '%s.docker-compose.yml' % self._key_env()
        if not local.path(env_file).exists():
            (echo['version: "3"'] > env_file)()
        return (
            'docker-compose.yml:%s.docker-compose.yml'
            % self._key_env())

    def _key_uid(self):
        return id['-u']().replace('\n', '')

    def _key_compose_project_name(self):
        return get_project_name()

    def _key_env(self):
        return self.env

    @property
    def env(self):
        # set current environment for creating file dev.docker-compose
        # TODO: use --env flag instead
        if not hasattr(self, '_env'):
            self._env = prompt('Current environment ?', default='dev')
        return self._env

    @property
    def keys(self):
        self._keys = {
            'UID': self._key_uid,
            'ENV': self._key_env,
            'COMPOSE_FILE': self._key_compose_file,
            'COMPOSE_PROJECT_NAME': self._key_compose_project_name,
        }
        return self._keys

    def generate(self):
        logger.info('Writing .env file')
        env = Environment.from_env_file('.')
        to_add = []
        for key, fun in self.keys.items():
            if env.get(key):
                logger.debug(
                    '%s already present in .env, not modified' % key)
            else:
                logger.debug('Adding %s to .env' % key)
                to_add.append('%s=%s' % (key, fun()))
        for line in to_add:
            # append line to file
            (echo[line] >> '.env')()


def get_project_name():
    env = Environment.from_env_file('.')
    return env.get(
        'COMPOSE_PROJECT_NAME',
        '%s_%s' % (slugify(local.env.user), slugify(local.cwd.name))
    )
