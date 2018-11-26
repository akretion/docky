# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from plumbum import cli
from .base import Docky, DockySub, raise_error


class DockyExec(object):

    root = cli.Flag(
        ["root"],
        help="Run or open as root",
        group = "Meta-switches")

    def _use_specific_user(self):
        return not self.root and self.project.user


@Docky.subcommand("run")
class DockyRun(DockySub, DockyExec):
    """Start services and enter in your dev container"""

    def _check_running(self):
        if self.project.get_containers(service=self.project.service):
            raise_error("This container is already running, kill it or "
                        "use open to go inside")

    def _main(self, *optionnal_command_line):
        self._check_running()
        self.proxy.start_if_needed()
        if self._use_specific_user():
            cmd = ['gosu', self.project.user]
        else:
            cmd = []
        if not optionnal_command_line:
            cmd.append('bash')
        else:
            cmd += list(optionnal_command_line)
        # Remove useless dead container before running a new one
        self._run(self.compose['rm', '-f'])
        self.project.show_access_url()
        self.project.create_volume()
        self._exec('docker-compose', [
            '-f', self.project.compose_file_path,
            '--project-name', self.project.name,
            'run', '--rm', '--service-ports', '--use-aliases',
            self.project.service] + cmd)


@Docky.subcommand("open")
class DockyOpen(DockySub, DockyExec):
    """Open a new session inside your dev container"""

    # Patch compose service to be make it working with docker-compose run

    def _main(self, service=None):
        cmd = ['bash']
        if not service:
            service = self.project.service
            if self._use_specific_user():
                cmd = ['gosu', self.project.user, 'bash']
        self._exec('dcpatched', [
            '-f', self.project.compose_file_path,
            '--project-name', self.project.name,
            'exec', service] + cmd)
