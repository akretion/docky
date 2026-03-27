# Copyright 2018-TODAY Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import sys
import tempfile
import threading
from os import getuid

from plumbum import cli
from python_on_whales import DockerClient, docker

from ..common.api import logger, raise_error
from ..common.url_opener import url_opener
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

    def _get_base_docker_env(self):
        return {
            "NOGOSU": "True",
        }

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


def find_free_port():
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@Docky.subcommand("run")
class DockyRun(DockyExec):
    """Start services and enter in your dev container"""

    volumes = cli.SwitchAttr(
        ["-v", "--volume"],
        str,
        help="Add a volume to the container, in the format host_path:container_path",
        group="Meta-switches",
        list=True,
    )

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

        docker_env = self._get_base_docker_env()
        volumes = [volume.split(":", 1) for volume in self.volumes]

        if self.kalong:
            global docker

            self.kalong_port = self.kalong_port or find_free_port()

            # As we can’t have service_ports and publish at the same time,
            # we have to use a temporary compose files to set up the port forwarding
            kalong_temp_compose_file = tempfile.NamedTemporaryFile(
                mode="w+", suffix=".yml", prefix="kalong_"
            )
            kalong_temp_compose_file.write(
                "services:\n"
                f"  {self.service}:\n"
                "    ports:\n"
                f"      - {self.kalong_port}:{self.kalong_port}\n"
            )
            kalong_temp_compose_file.flush()
            docker = DockerClient(
                compose_files=[
                    *self.project._get_compose_files(),
                    kalong_temp_compose_file.name,
                ]
            )

            socket_name = (
                self.kalong_url_socket
                or f"/run/user/{getuid()}/kalong_{self.project.name}.sock"
            )

            threading.Thread(
                target=url_opener, args=(socket_name,), daemon=True
            ).start()

            docker_env.update(
                # Inside docker, bind to all interfaces
                KALONG_HOST="0.0.0.0",
                # Outside docker, use the provided host (which should be localhost)
                KALONG_FRONT_HOST=self.kalong_host,
                KALONG_PORT=self.kalong_port,
                # Path of the socket used to forward the kalong url to the host browser
                KALONG_URLSOCKET=socket_name,
                # Set up kalong as the default breakpoint handler
                PYTHONBREAKPOINT="kalong.breakpoint",
            )
            volumes.append((socket_name, socket_name))

        # Remove useless dead container before running a new one
        docker.compose.rm()
        self.project.display_service_tooltip()
        self.project.create_volume()

        docker.compose.run(
            service=self.service,
            remove=True,
            service_ports=True,
            use_aliases=True,
            envs=docker_env,
            volumes=volumes,
            command=self.cmd,
        )


@Docky.subcommand("open")
class DockyOpen(DockyExec):
    """Open a new session inside your dev container"""

    def _main(self, *optionnal_command_line):
        super()._main(*optionnal_command_line)
        docker.compose.execute(
            service=self.service,
            index=0,
            envs=self._get_base_docker_env(),
            command=self.cmd,
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
