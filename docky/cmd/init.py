# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from plumbum import cli
from plumbum.cli.terminal import ask


from .base import Docky
from ..common.generator import GenerateComposeFile, GenerateEnvFile

TEMPLATE_SERVICE = ['odoo']


@Docky.subcommand("init")
class DockyInit(cli.Application):
    """Initalize a project"""

    def main(self, *args, **kwargs):
        self._generate_env()
        self._generate_dev_docker_compose_file()

    def _generate_dev_docker_compose_file(self):
        for service in TEMPLATE_SERVICE:
            generate = ask(
                "Do you want to generate docker-compose.yml "
                "automatically for %s" % service,
                default=True)
            if generate:
                return GenerateComposeFile(service).generate()

    def _generate_env(self):
        generate = ask(
            "Do you want to generate .env file ?", default=True)
        if generate:
            return GenerateEnvFile().generate()
