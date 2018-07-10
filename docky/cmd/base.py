# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from plumbum import cli, local
from plumbum.commands.modifiers import FG
from compose.cli.command import get_project
from compose.project import OneOffFilter
from pwd import getpwnam
import logging
import os

from ..common.api import logger, raise_error
from ..common.config import UserConfig, ProjectEnvironment


class Docky(cli.Application):
    PROGNAME = "docky"
    VERSION = '3.0.7'
    SUBCOMMAND_HELPMSG = None

    dryrun = cli.Flag(
        ["dry-run"],
        help="Dry run mode",
        group = "Meta-switches")
    force_env = cli.SwitchAttr(
        ["e", "env"],
        help="Environment flag",
        group = "Switches")

    def _run(self, cmd, retcode=FG):
        """Run a command in a new process and log it"""
        logger.debug(str(cmd).replace('/usr/local/bin/', ''))
        if (self.dryrun):
            logger.info(cmd)
            return True
        return cmd & retcode

    def _exec(self, cmd, args=[]):
        """Run a command in the same process and log it
        this will replace the current process by the cmd"""
        logger.debug(cmd + ' '.join(args))
        if (self.dryrun):
            logger.info("os.execvpe (%s, %s, env)", cmd, [cmd] + args)
            return True
        os.execvpe(cmd, [cmd] + args, local.env)

    def __init__(self, executable):
        super(Docky, self).__init__(executable)
        self.user_config = UserConfig()
        local.env['UID'] = str(getpwnam(local.env.user).pw_uid)
        self.env = self.force_env or self.user_config.env

        if self.user_config.verbose:
            self.set_log_level()
            logger.debug(
                'Start in verbose mode. You can change the default '
                'value in ~/.docky/config.yml')

        # TODO maybe remove me with the code of downloading
        # the maintainer tools
        self.shared_folder = os.path.join(
            self.user_config.home, '.docky', 'shared')

    @cli.switch("--verbose", help="Verbose mode", group = "Meta-switches")
    def set_log_level(self):
        logger.setLevel(logging.DEBUG)
        logger.debug('Verbose mode activated')


class DockySub(cli.Application):

    def _exec(self, *args, **kwargs):
        self.parent._exec(*args, **kwargs)

    def _run(self, *args, **kwargs):
        self.parent._run(*args, **kwargs)

    def get_containers(self, service=None):
        project = get_project(
            '.', [self.project.compose_file_path],
            project_name=self.project.name)
        kwargs = {'one_off': OneOffFilter.include}
        if service:
            kwargs['service_names'] = [service]
        return project.containers(**kwargs)

    def main(self, *args, **kwargs):
        self.env = self.parent.env
        self.project = ProjectEnvironment(self.env)
        self.compose = local['docker-compose'][
            '-f', self.project.compose_file_path,
            '--project-name', self.project.name]
        self._main(*args, **kwargs)

DockySub.unbind_switches("--help-all", "-v", "--version")
