# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import yaml
from plumbum.cli.terminal import ask
from plumbum import local
from .generator import GenerateComposeFile
from .api import logger


DEFAULT_CONF = {
    "verbose": True,
    "env": "dev",
}

DOCKY_PATH = 'docky.yml'
DOCKER_COMPOSE_PATH = 'docker-compose.yml'


# TODO refactor code using local object of plumbum instead of os
class DockyConfig(object):

    def _get_home(self):
        return os.path.expanduser("~")

    def __init__(self):
        super(DockyConfig, self).__init__()
        self.home = self._get_home()
        self.config_path = os.path.join(self.home, '.docky', 'config.yml')
        current_config = self._get_config()
        config = self._get_config_with_default_value(current_config)

        if current_config != config:
            self._update_config_file(config)
        self.env = config.get('env')
        self.verbose = config.get('verbose')

    def _get_config(self):
        if os.path.isfile(self.config_path):
            return yaml.safe_load(open(self.config_path, 'r'))
        else:
            return {}

    def _get_config_with_default_value(self, current_config):
        config = DEFAULT_CONF.copy()
        for key, value in DEFAULT_CONF.items():
            if key in current_config:
                config[key] = current_config[key]
        return config

    def _update_config_file(self, config):
        logger.info("The Docky Configuration have been updated, "
                    "please take a look to the new config file")
        config_file = open(self.config_path, 'w')
        config_file.write(yaml.dump(config, default_flow_style=False))
        logger.info("Update default config file at %s", self.config_path)


class ProjectEnvironment(object):

    def __init__(self, env):
        self.env = env
        self._parse_docky_file()
        self.compose_file_path = self._get_config_path()
        if self.env == 'dev':
            if not local.path(self.compose_file_path).isfile():
                self._generate_dev_docker_compose_file()
        self.name = self._get_project_name()

    def _parse_docky_file(self):
        if os.path.isfile(DOCKY_PATH):
            config = yaml.safe_load(open(DOCKY_PATH, 'r'))
            self.service = config.get('service')
            self.user = config.get('user')
        else:
            raise_error(
                '%s file is missing. Minimal file is a yaml file with:\n'
                ' service: your_service\nex:\n service: odoo' % DOCKY_PATH)

    def run_hook(self, cls):
        def getsubclass(cls, service):
            for subcls in cls.__subclasses__():
                print("subcls", subcls._service)
                if subcls._service == service:
                    return subcls
                else:
                    service_cls = getsubclass(subcls, service)
                    if service_cls:
                        return service_cls
            return None
        service_cls = getsubclass(cls, self.main_service)
        if not service_cls:
            service_cls = cls
        return service_cls(self, logger).run()

    def _get_config_path(self):
        config_path = '.'.join([self.env, DOCKER_COMPOSE_PATH])
        if self.env == 'dev':
            return config_path
        elif local.path(config_path).is_file():
            return config_path
        elif local.path(DOCKER_COMPOSE_PATH).is_file():
            return DOCKER_COMPOSE_PATH
        else:
            raise_error(
                "There is not %s.%s or %s file, please add one"
                % (self.env, DOCKER_COMPOSE_PATH, DOCKER_COMPOSE_PATH))

    def _generate_dev_docker_compose_file(self):
        generate = ask(
            "There is not dev.docker-compose.yml file.\n"
            "Do you want to generate one automatically",
            default=True)
        if generate:
            GenerateComposeFile(self.service).generate()
        else:
            raise_error("No dev.docker-compose.yml file, abort!")

    def _get_project_name(self):
        return "%s_%s" % (local.env.user, local.cwd.name)
