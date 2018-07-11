# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from plumbum import cli
from .base import Docky, DockySub, raise_error, logger
from ..common.config import DockerComposeConfig
import docker
import yaml

client = docker.from_env()

DOCKY_NETWORK_NAME = 'dy'
DOCKY_NETWORK_SUBNET = '172.30.0.0/16'
DOCKY_NETWORK_GATEWAY = '172.30.0.1'
DOCKY_NETWORK_OPTIONS = {
    'com.docker.network.bridge.name': DOCKY_NETWORK_NAME,
    'com.docker.network.bridge.host_binding_ipv4': '127.0.0.1',
}


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

    def _set_local_dev_network(self):
        net = DOCKY_NETWORK_NAME
        if not client.networks.list(net):
            ipam_pool = docker.types.IPAMPool(
                subnet=DOCKY_NETWORK_SUBNET,
                iprange=DOCKY_NETWORK_SUBNET,
                gateway=DOCKY_NETWORK_GATEWAY,
            )
            ipam_config = docker.types.IPAMConfig(
                pool_configs=[ipam_pool])

            logger.info("Create '.%s' network" % net)

            client.networks.create(
                net,
                driver="bridge",
                ipam=ipam_config,
                options=DOCKY_NETWORK_OPTIONS,
            )

    def _check_running(self):
        if self.get_containers(service=self.project.service):
            raise_error("This container is already running, kill it or "
                        "use open to go inside")

    def _main(self, *optionnal_command_line):
        self._check_running()
        if self._use_specific_user():
            cmd = ['gosu', self.project.user]
        else:
            cmd = []
        if not optionnal_command_line:
            cmd.append('bash')
        else:
            cmd += list(optionnal_command_line)
        if self.env == 'dev':
            self._set_local_dev_network()
        # Remove useless dead container before running a new one
        self._run(self.compose['rm', '-f'])
        compose_config = DockerComposeConfig(self.project)
        compose_config.show_access_url()
        compose_config.create_volume()
        self._exec('docker-compose', [
            '-f', self.project.compose_file_path,
            '--project-name', self.project.name,
            'run', '--rm', '--service-ports',
            self.project.service] + cmd)


@Docky.subcommand("open")
class DockyOpen(DockySub, DockyExec):
    """Open a new session inside your dev container"""

    def _main(self, *args):
        container = self.get_containers(service=self.project.service)
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
