# Copyright 2018-TODAY Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from python_on_whales import docker
from plumbum import local
import os
from .api import logger


class Project(object):

    def __init__(self):
        try:
            self.project = docker.compose.config(return_json=True)
        except Exception as e:
            logger.error("Fail to load the configuration, try to validate it")
            # If we fail to read the config file, it's mean that the config
            # is not valid. In order to raise the same error as docker compose
            # we launch the cmd to validate the config
            os.execvpe("docker",  [
                "docker", "--log-level", "ERROR", "compose", "config"
                ], local.env)

        self.name = self.project.get("name")
        self.service = self._get_main_service(self.project)

    def _get_main_service(self, project):
        """main_service has docky.main.service defined in
        his label."""
        for service in project.get("services"):
            labels = project["services"][service].get("labels")
            if labels and labels.get("docky.main.service"):
                return service

    def display_service_tooltip(self):
        for _name, service in self.project.get("services").items():
            docky_help = service.get("labels", {}).get("docky.help")
            if docky_help:
                logger.info(docky_help)

    def create_volume(self):
        """Mkdir volumes if they don't exist yet.

        Only apply to external volumes.
        docker compose will create it but the owner will be root
        so we have to do it ourselves with the right owner"""
        for service_name, service in self.project.get("services").items():
            for volume in service.get("volumes", []):
                if volume["type"] == "bind":
                    path = local.path(local.env.expand(volume["source"]))
                    if not path.exists():
                        logger.info(
                            "Create missing directory %s for service %s",
                            path, service_name)
                        path.mkdir()

    def get_user(self, service_name):
        labels = self.project["services"].get(service_name).get("labels")
        if labels:
            return labels.get("docky.user")
