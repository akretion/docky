# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from plumbum import cli, local
from plumbum.cli.terminal import prompt

from .base import Docky
from plumbum.cmd import id


@Docky.subcommand("init")
class DockyInit(cli.Application):
    """Initalize the file '.env' of an existing project"""
    def _uid(self):
        return id['-u']().replace('\n', '')

    def main(self):
        if not local.path(".env").is_file():
            env = prompt("Choose the env to init (dev, prod...)?", default="dev")
            project_name = prompt(
                "Define the project name?", default=local.path().parts[-1])
            with open(".env", "w") as f:
                f.write(
                    f"UID={self._uid()}\n"
                    f"COMPOSE_FILE={env}.docker-compose.yml:docker-compose.yml\n"
                    f"COMPOSE_PROJECT_NAME={project_name}\n"
                    "COMPOSE_DOCKER_CLI_BUILD=1\n"
                    f"ENV={env}")
