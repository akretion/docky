# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from compose.project import OneOffFilter
from compose.cli import command
from compose.config.errors import ComposeFileNotFound
from plumbum import local

from .api import logger


class Project(object):

    def __init__(self):
        try:
            self.project = command.project_from_options('.', {})
        except ComposeFileNotFound:
            print("No docker-compose found, create one with :")
            print('$ docky init')
            exit(-1)

        self.name = self.project.name
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

    def get_containers(self, service=None):
        kwargs = {'one_off': OneOffFilter.include}
        if service:
            kwargs['service_names'] = [service]
        return self.project.containers(**kwargs)

    def show_access_url(self):
        for service in self.project.services:
            labels = service.options.get('labels', {})
            if labels.get('docky.access.help'):
                # TODO remove after some versions
                logger.warning(
                    "'docky.access.help' is replaced by 'docky.help'. "
                    "Please update this key in your docker files.")
            if labels.get('docky.help'):
                logger.info(labels.get('docky.help'))

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
        if labels:
            return labels.get('docky.user', None)
