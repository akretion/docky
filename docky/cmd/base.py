# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from plumbum import cli, local
from plumbum.commands.modifiers import FG
import logging
import os

from ..common.api import logger
from ..common.project import Project


class Docky(cli.Application):
    PROGNAME = "docky"
    VERSION = '7.0.3'
    SUBCOMMAND_HELPMSG = None

    def _run(self, cmd, retcode=FG):
        """Run a command in a new process and log it"""
        logger.debug(str(cmd).replace('/usr/local/bin/', ''))
        return cmd & retcode

    def _exec(self, cmd, args=[]):
        """Run a command in the same process and log it
        this will replace the current process by the cmd"""
        logger.debug(cmd + ' '.join(args))
        os.execvpe(cmd, [cmd] + args, local.env)

    @cli.switch("--verbose", help="Verbose mode", group="Meta-switches")
    def set_log_level(self):
        logger.setLevel(logging.DEBUG)
        logger.debug('Verbose mode activated')


class DockySub(cli.Application):
    _project_specific = True

    def _exec(self, *args, **kwargs):
        self.parent._exec(*args, **kwargs)

    def _run(self, *args, **kwargs):
        self.parent._run(*args, **kwargs)

    def _init_project(self):
        self.project = Project()
        self.compose = local['docker-compose']

    def main(self, *args, **kwargs):
        if self._project_specific:
            self._init_project()
        self._main(*args, **kwargs)


class DockySubNoProject(DockySub):
    _project_specific = False


DockySub.unbind_switches("--help-all", "-v", "--version")
