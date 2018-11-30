# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from plumbum import cli, local
from plumbum.commands.modifiers import FG
from pwd import getpwnam
import logging
import os

from ..common.api import logger, raise_error
from ..common.config import DockyConfig
from ..common.project import Project
from ..common.proxy import Proxy


class Docky(cli.Application):
    PROGNAME = "docky"
    VERSION = '5.0.2'
    SUBCOMMAND_HELPMSG = None

    force_env = cli.SwitchAttr(
        ["e", "env"],
        help="Environment flag",
        group = "Switches")

    def _run(self, cmd, retcode=FG):
        """Run a command in a new process and log it"""
        logger.debug(str(cmd).replace('/usr/local/bin/', ''))
        return cmd & retcode

    def _exec(self, cmd, args=[]):
        """Run a command in the same process and log it
        this will replace the current process by the cmd"""
        logger.debug(cmd + ' '.join(args))
        os.execvpe(cmd, [cmd] + args, local.env)

    def __init__(self, executable):
        super(Docky, self).__init__(executable)
        self.config = DockyConfig()
        if self.config.verbose:
            self.set_log_level()
            logger.debug(
                'Start in verbose mode. You can change the default '
                'value in ~/.docky/config.yml')

    @cli.switch("--verbose", help="Verbose mode", group = "Meta-switches")
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
        self.project = Project(self.env, self.parent.config)
        self.project.build_network()
        self.compose = local['docker-compose'][
            '-f', self.project.compose_file_path,
            '--project-name', self.project.name]

    def main(self, *args, **kwargs):
        local.env['UID'] = str(getpwnam(local.env.user).pw_uid)
        self.env = self.parent.force_env or self.parent.config.env
        self.proxy = Proxy(self.parent.config)
        if self._project_specific:
            self._init_project()
        self._main(*args, **kwargs)


class DockySubNoProject(DockySub):
    _project_specific = False


DockySub.unbind_switches("--help-all", "-v", "--version")
