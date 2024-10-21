# Copyright 2018-TODAY Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import sys
import subprocess
from plumbum import cli
from .base import Docky, DockySub
from ..common.api import raise_error, logger

from python_on_whales import docker


class DockyExec(DockySub):

    root = cli.Flag(
        ["root"],
        help="Run or open as root",
        group="Meta-switches")
    service = cli.SwitchAttr(["service"])

    def _use_specific_user(self, service):
        return "root" if self.root else self.project.get_user(service)

    def _get_cmd_line(self, optionnal_command_line):
        user = self._use_specific_user(self.service)
        cmd = []
        if user:
            cmd = ["gosu", user]
        if not optionnal_command_line:
            cmd.append("bash")
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
        for service in docker.compose.ps(services=[self.service], all=True):
            if service.state.status == "exited":
                # In case that you have used "docker compose run" without the
                # option "--rm" you can have exited container
                # we purge them here as they are useless
                service.remove()
            else:
                raise_error("This container is already running, kill it or "
                            "use open to go inside")

    def _main(self, *optionnal_command_line):
        super()._main(*optionnal_command_line)
        self._check_running()
        # Remove useless dead container before running a new one
        self._run(self.compose["rm", "-f"])
        self.project.display_service_tooltip()
        self.project.create_volume()
        # Default command
        docky_cmd = ["run", "--rm", "--service-ports", "--use-aliases", "-e", "NOGOSU=True", self.service] + self.cmd

        self._exec("docker", ["compose"] + docky_cmd)

        # TODO: Should we use python-on-whales commands?
        #  Its possible make
        # docker.compose.run(self.project.name, and other parameters)
        # But until now was not possible make the same command as above,
        # if its possible we should consider the option to use it.
        # https://gabrieldemarmiesse.github.io/python-on-whales/sub-commands/compose/


@Docky.subcommand("open")
class DockyOpen(DockyExec):
    """Open a new session inside your dev container"""

    # Patch compose service to be make it working with docker-compose run

    def _main(self, *optionnal_command_line):
        super()._main(*optionnal_command_line)
        # self._exec("dcpatched", ["exec", "-e", "NOGOSU=True", self.service] + self.cmd)

        # Get Project Name
        # Example:     docky-odoo-brasil-14      odoo
        project_name = self.project.name + "-" + self.project.service

        # Get User
        user = self._use_specific_user(self.service)

        # Get Container ID
        command = "docker ps -aqf name=" + project_name
        # Example of return value
        # b'b5db9db21381\n'
        # Option text=true return as string instead of bytes and strip remove break line
        # TODO: Is there a better way to do it, for example with Plumbum?
        container_id = subprocess.check_output(command, shell=True,text=True).strip()

        self._exec("docker", ["exec", "-u", user, "-it", container_id, "/bin/bash"])

@Docky.subcommand("system")
class DockySystem(DockyExec):
    """
    Check your System Infos:
    OS Type, Kernel, OS, Docker, Docker Compose, and Docky versions.
    """
    def _main(self):
        # Info
        infos = docker.system.info()
        # OS Type
        logger.info("OS Type " + infos.os_type)
        # Kernel Version
        logger.info("Kernel Version " + infos.kernel_version)
        # Operation System
        logger.info("OS " + infos.operating_system)
        # Python Version
        logger.info("Python Version " + sys.version)
        # Docker Version
        logger.info("Docker Version " + infos.server_version)
        # Docker Compose Version
        logger.info(docker.compose.version())
        # Docky Version
        logger.info("Docky Version " + Docky.VERSION)
