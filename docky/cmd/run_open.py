# Copyright 2018-TODAY Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import sys
from os import getuid

from plumbum import cli
from python_on_whales import docker

from ..common.api import logger, raise_error
from .base import Docky, DockySub


class DockyExec(DockySub):
    root = cli.Flag(["root"], help="Run or open as root", group="Meta-switches")
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
                "in your docker-compose file."
            )
        self.cmd = self._get_cmd_line(optionnal_command_line)


DOCKER_DOWN_STATUS = ["created", "exited"]


def find_free_port(start_port):
    import socket

    port = start_port
    while port < 65535:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", port)) != 0:
                return port
            port += 1
    raise RuntimeError("No free port found")


@Docky.subcommand("run")
class DockyRun(DockyExec):
    """Start services and enter in your dev container"""

    kalong = cli.Flag(
        ["-k", "--kalong"],
        help="Set up kalong in docker and forward url to open in your browser",
        group="Meta-switches",
    )
    kalong_host = cli.SwitchAttr(
        ["--kalong_host"],
        str,
        help="Host of the kalong server",
        group="Meta-switches",
        default="localhost",
    )
    kalong_port = cli.SwitchAttr(
        ["--kalong_port"],
        str,
        help="Port of the kalong server, default to first free port after 50000",
        group="Meta-switches",
    )
    kalong_url_socket = cli.SwitchAttr(
        ["--kalong_url_socket"],
        str,
        help="Path of the socket used to forward url to open in your browser, "
        "default to /run/user/UID/kalong_PROJECTNAME.sock",
        group="Meta-switches",
    )

    def _check_running(self):
        for service in docker.compose.ps(services=[self.service], all=True):
            if service.state.status in DOCKER_DOWN_STATUS:
                # In case that you have used "docker compose run" without the
                # option "--rm" you can have exited container
                # we purge them here as they are useless
                service.remove()
            else:
                raise_error(
                    "This container is already running, kill it or "
                    "use open to go inside"
                )

    def _main(self, *optionnal_command_line):
        super()._main(*optionnal_command_line)
        self._check_running()
        # Remove useless dead container before running a new one
        self._run(self.compose["rm", "-f"])
        self.project.display_service_tooltip()
        self.project.create_volume()

        base_cmd = [
            "run",
            "--rm",
            "--service-ports",
            "--use-aliases",
            "-e",
            "NOGOSU=True",
        ]

        if self.kalong:
            import threading

            from ..common.url_opener import url_opener

            if self.kalong_port is None:
                self.kalong_port = find_free_port(50000)

            socket_name = (
                self.kalong_url_socket
                or f"/run/user/{getuid()}/kalong_{self.project.name}.sock"
            )

            threading.Thread(
                target=url_opener, args=(socket_name,), daemon=True
            ).start()

            # Can’t use service ports here since we need to publish kalong port
            base_cmd = [cmd for cmd in base_cmd if cmd != "--service-ports"]

            base_cmd += [
                "-p",
                f"{self.kalong_port}:{self.kalong_port}",
                "-v",
                f"{socket_name}:{socket_name}",
                "-e",
                "KALONG_HOST=0.0.0.0",  # Inside docker, bind to all interfaces
                "-e",
                f"KALONG_FRONT_HOST={self.kalong_host}",  # Outside docker, use the provided host (which should be localhost)
                "-e",
                f"KALONG_PORT={self.kalong_port}",
                "-e",
                "PYTHONBREAKPOINT=kalong.breakpoint",
                "-e",
                f"KALONG_URLSOCKET={socket_name}",
            ]

        # Default command
        docky_cmd = (
            base_cmd
            + [
                self.service,
            ]
            + self.cmd
        )

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

    def _main(self, *optionnal_command_line):
        super()._main(*optionnal_command_line)
        self._exec(
            "docker",
            [
                "compose",
                "exec",
                "-e",
                "NOGOSU=True",
                self.service,
            ]
            + self.cmd,
        )


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
