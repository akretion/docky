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
    """Start services and enter in your dev container

    After running the command you will be inside the container and
    you will have access to the ak cmd (see ak documenation)
    main command are 'ak run' and 'ak build'

    Note: the container is accessible with the following url :
    http://my_project.vd and http://my_plugin.my_project.vd
    """

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
            'run', '--rm', '--service-ports',
            self.project.service] + cmd)


@Docky.subcommand("open")
class DockyOpen(DockySub, DockyExec):
    """Open a new session inside your dev container"""

    def _main(self, *args):
        container = self.project.get_containers(service=self.project.service)
        if container:
            cmd = ["exec", "-ti", container[0].name]
            if self._use_specific_user():
                cmd += ['gosu', self.project.user, 'bash']
            else:
                cmd.append('bash')
            self._exec('docker', cmd)
        else:
            raise_error(
                "No container found for the service %s" % self.main_service)
