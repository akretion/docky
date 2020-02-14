# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from plumbum import cli
from .base import Docky, DockySub
from ..common.api import raise_error


class DockyExec(DockySub):

    root = cli.Flag(
        ["root"],
        help="Run or open as root",
        group="Meta-switches")
    service = cli.SwitchAttr(["service"])

    def _use_specific_user(self, service):
        return not self.root and self.project.get_user(service)

    def _get_cmd_line(self, optionnal_command_line):
        user = self._use_specific_user(self.service)
        cmd = []
        if user:
            cmd = ['gosu', user]
        if not optionnal_command_line:
            cmd.append('bash')
        else:
            cmd += list(optionnal_command_line)
        return cmd

    def _main(self, *optionnal_command_line):
        if not self.service:
            self.service = self.project.service
        if not self.service:
            raise_error(
                "Fail to define the service to start\n"
                "No service '--service=foo' have been pass\n"
                "And there is no label: docky.main.service: True "
                "in your docker-compose file.")
        self.cmd = self._get_cmd_line(optionnal_command_line)


@Docky.subcommand("run")
class DockyRun(DockyExec):
    """Start services and enter in your dev container"""

    def _check_running(self):
        if self.project.get_containers(service=self.service):
            raise_error("This container is already running, kill it or "
                        "use open to go inside")

    def _main(self, *optionnal_command_line):
        super()._main(*optionnal_command_line)
        self._check_running()
        # Remove useless dead container before running a new one
        self._run(self.compose['rm', '-f'])
        self.project.display_service_tooltip()
        self.project.create_volume()
        self._exec('docker-compose', [
            'run', '--rm', '--service-ports', '--use-aliases',
            self.service] + self.cmd)


@Docky.subcommand("open")
class DockyOpen(DockyExec):
    """Open a new session inside your dev container"""

    # Patch compose service to be make it working with docker-compose run

    def _main(self, *optionnal_command_line):
        super()._main(*optionnal_command_line)
        self._exec('dcpatched', [
            'exec', self.service] + self.cmd)
