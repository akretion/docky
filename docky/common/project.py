# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from compose.cli.command import get_project
from compose.project import OneOffFilter
from plumbum import local
from plumbum.cli.terminal import ask
import docker
import yaml
import os

from .api import logger, raise_error
from .generator import GenerateComposeFile

client = docker.from_env()

DOCKER_COMPOSE_PATH = 'docker-compose.yml'
TEMPLATE_SERVICE = ['odoo']

class Project(object):

    def __init__(self, env, docky_config):
        self.env = env
        self.docky_config = docky_config
        self.compose_file_path = self._get_config_path()
        if self.env == 'dev':
            if not local.path(self.compose_file_path).isfile():
                self._generate_dev_docker_compose_file()
        self.name = self._get_project_name()
        self.loaded_config = None
        self.service = self._get_main_service()

    def _get_main_service(self):
        for name, service in self.config['services'].items():
            for label, value in service.get('labels', {}).items():
                if label == 'docky.main.service' and value is True:
                    return name

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
        print("There is not dev.docker-compose.yml file.\n")
        for service in TEMPLATE_SERVICE:
            generate = ask(
                "Do you want to generate one automatically for %s" % service,
                default=True)
            if generate:
                return GenerateComposeFile(service).generate()
        raise_error("No dev.docker-compose.yml file, abort!")

    def _get_project_name(self):
        return local.env.get(
            'COMPOSE_PROJECT_NAME',
            '%s_%s' % (local.env.user, local.cwd.name)
        )

    def get_containers(self, service=None):
        project = get_project(
            '.', [self.compose_file_path],
            project_name=self.name)
        kwargs = {'one_off': OneOffFilter.include}
        if service:
            kwargs['service_names'] = [service]
        return project.containers(**kwargs)

    @property
    def config(self):
        if not self.loaded_config:
            self.loaded_config = yaml.safe_load(
                open(self.compose_file_path, 'r'))
        return self.loaded_config

    def show_access_url(self):
        for name, service in self.config['services'].items():
            for label, value in service.get('labels', {}).items():
                if label == 'docky.access.help':
                    logger.info(
                        "The service %s is accessible on %s"
                        % (name, value))

    def create_volume(self):
        for name, service in self.config['services'].items():
            if 'volumes' in service:
                for volume_path in service['volumes']:
                    volume = volume_path.split(':')[0]
                    if any([volume.startswith(c) for c in ['.', '/', '$']]):
                        path = local.path(local.env.expand(volume))
                        if not path.exists():
                            logger.info(
                                "Create missing directory %s for service %s",
                                path, name)
                            path.mkdir()

    def get_user(self, service):
        for label, value in \
                self.config['services'][service].get('labels', {}).items():
            if label == 'docky.user':
                return value
        return None
