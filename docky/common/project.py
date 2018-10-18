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

DOCKY_PATH = 'docky.yml'
DOCKER_COMPOSE_PATH = 'docker-compose.yml'


class Project(object):

    def __init__(self, env, docky_config):
        self.env = env
        self.docky_config = docky_config
        self._parse_docky_file()
        self.compose_file_path = self._get_config_path()
        if self.env == 'dev':
            if not local.path(self.compose_file_path).isfile():
                self._generate_dev_docker_compose_file()
        self.name = self._get_project_name()
        self.loaded_config = None

    def _parse_docky_file(self):
        if os.path.isfile(DOCKY_PATH):
            config = yaml.safe_load(open(DOCKY_PATH, 'r'))
            self.service = config.get('service')
            self.user = config.get('user')
        else:
            raise_error(
                '%s file is missing. Minimal file is a yaml file with:\n'
                ' service: your_service\nex:\n service: odoo' % DOCKY_PATH)

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
            for env in service.get('environment', []):
                if 'VIRTUAL_HOST=' in env:
                    dns = env.replace('VIRTUAL_HOST=', '')
                    logger.info(
                        "The service %s is accessible on http://%s"
                        % (name, dns))

    def create_volume(self):
        for name, service in self.config['services'].items():
            if 'volumes' in service:
                for volume_path in service['volumes']:
                    volume = volume_path.split(':')[0]
                    if volume.startswith('.') or volume.startswith('/'):
                        path = local.path(volume)
                        if not path.exists():
                            logger.info(
                                "Create missing directory %s for service %s",
                                volume, name)
                            local.path(volume).mkdir()

    def build_network(self):
        network = self.docky_config.network
        if not network:
            logger.info("No network define, skip it")
        gateway = '.'.join(network['subnet'].split('.')[0:3] + ["1"])
        for net in client.networks.list(network['name']):
            if net.name == network['name']:
                return
        ipam_pool = docker.types.IPAMPool(
            subnet=network['subnet'],
            iprange=network['subnet'],
            gateway=gateway,
        )
        ipam_config = docker.types.IPAMConfig(
            pool_configs=[ipam_pool])

        logger.info("Create '.%s' network" % network['name'])

        client.networks.create(
            network['name'],
            driver="bridge",
            ipam=ipam_config,
            options=network['options'],
        )
