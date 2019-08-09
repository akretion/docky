# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from compose.cli.command import get_project
from compose.project import OneOffFilter
from plumbum import local
from plumbum.cli.terminal import ask
from compose.cli import command
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
        self.compose_file_path = self._get_config_path(self.env)
        if self.env == 'dev':
            if not local.path(self.compose_file_path).isfile():
                self._generate_dev_docker_compose_file()
        self.project = command.project_from_options(
            '.', {'--file': [self.compose_file_path]})
        self.name = self._get_project_name(self.project)
        self.loaded_config = None
        self.service = self._get_main_service(self.project)

    def _get_main_service(self, project):
        """main_service has docky.main.service defined in
        his label."""
        for service in project.services:
            labels = service.options.get('labels', {})
            # service.labels() do not contain docky.main.service
            # see also compose.service.merge_labels
            if labels.get('docky.main.service', False):
                return service.name

    def _get_config_path(self, env):
        # TODO a virer et utiliser --files de compose
        config_path = '.'.join([env, DOCKER_COMPOSE_PATH])
        if env == 'dev':
            return config_path
        elif local.path(config_path).is_file():
            return config_path
        elif local.path(DOCKER_COMPOSE_PATH).is_file():
            return DOCKER_COMPOSE_PATH
        else:
            raise_error(
                "There is not %s.%s or %s file, please add one"
                % (env, DOCKER_COMPOSE_PATH, DOCKER_COMPOSE_PATH))

    def _generate_dev_docker_compose_file(self):
        print("There is not dev.docker-compose.yml file.\n")
        for service in TEMPLATE_SERVICE:
            generate = ask(
                "Do you want to generate one automatically for %s" % service,
                default=True)
            if generate:
                return GenerateComposeFile(service).generate()
        raise_error("No dev.docker-compose.yml file, abort!")

    def _get_project_name(self, project):
        # TODO return proj.name instead
        return local.env.get(
            'COMPOSE_PROJECT_NAME',
            '%s_%s' % (local.env.user, local.cwd.name)
        )

    def get_containers(self, service=None):
        kwargs = {'one_off': OneOffFilter.include}
        if service:
            kwargs['service_names'] = [service]
        return self.project.containers(**kwargs)

    @property
    def config(self):
        # TODO avirer !
        if not self.loaded_config:
            self.loaded_config = yaml.safe_load(
                open(self.compose_file_path, 'r'))
        return self.loaded_config

    def show_access_url(self):
        for service in self.project.services:
            labels = service.options.get('labels', {})
            url = labels.get('docky.access.help', False)
            if url:
                logger.info(
                    "The service %s is accessible on %s"
                    % (service.name, url))

    def create_volume(self):
        """Mkdir volumes if they don't exist yet.

        Only apply to external volumes.
        docker-compose up do not attemps to create it
        so we have to do it ourselves"""
        for service in self.project.services:
            for volume in service.options.get('volumes', []):
                if volume.external:
                    path = local.path(local.env.expand(volume.external))
                    if not path.exists():
                        logger.info(
                            "Create missing directory %s for service %s",
                            path, service.name)
                        path.mkdir()

    def get_user(self, service_name):
        service = self.project.get_service(name=service_name)
        labels = service.options.get('labels')
        return labels.get('docky.user', None)
