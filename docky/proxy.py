# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .main import (
    Docky,
    DockySub,
    raise_error,
    logger,
    DOCKY_NETWORK_NAME,
)

import docker

client = docker.from_env()

DOCKY_PROXY_IMAGE = "quay.io/akretion/docky-proxy:20180507"
DOCKY_PROXY_NAME = "docky-proxy"


@Docky.subcommand("proxy")
class DockyProxy(DockySub):
    """Start/Restart/Stop your docky proxy"""

    def _main(self, *args):
        if not self.nested_command:
            raise_error("Please specify an action, start/stop/restart")


class DockyProxySub(DockySub):

    def __init__(self, executable):
        super(DockyProxySub, self).__init__(executable)
        self.container = self._get_container()

    def _get_container(self):
        container = client.containers.list(
            all=True,
            filters={'name': DOCKY_PROXY_NAME})
        return container[0] if container else None

    def _restart(self):
        if self.container.status != 'running':
            logger.info("Restart docky proxy")
            self.container.restart()

    def _start(self):
        logger.info("Start Docky proxy")
        client.containers.run(
            DOCKY_PROXY_IMAGE,
            hostname=DOCKY_PROXY_NAME,
            name=DOCKY_PROXY_NAME,
            network_mode=DOCKY_NETWORK_NAME,
            volumes=[
                "/var/run/docker.sock:/tmp/docker.sock:ro",
                "/etc/hosts:/app/hosts",
                ],
                detach=True)


@DockyProxy.subcommand("start")
class DockyProxyStart(DockyProxySub):
    """Start your docky proxy"""

    def _main(self, *args):
        if not self.container:
            self._start()
        elif self.container.status != 'running':
            logger.info(
                "A container already exist but is not running. Restart it")
            self._restart()
        else:
            logger.info("Proxy is already running, skip")


@DockyProxy.subcommand("stop")
class DockyProxyStop(DockyProxySub):
    """Stop your docky proxy"""

    def _main(self, *args):
        if not self.container:
            logger.info("Proxy is already stopped, skip")
        else:
            logger.info("Stop the Proxy")
            self.container.stop()


@DockyProxy.subcommand("restart")
class DockyProxyRestart(DockyProxySub):
    """Restart your docky proxy"""

    def _main(self, *args):
        if not self.container:
            logger.info("Their is no proxy start it")
            self._start()
        else:
            self._restart()


@DockyProxy.subcommand("status")
class DockyProxyStatus(DockyProxySub):
    """Get the status of your docky proxy"""

    def _main(self, *args):
        if self.container:
            status = self.container.status
        else:
            status = 'container do not exist'
        logger.info('Proxy status: %s', status)


@DockyProxy.subcommand("kill")
class DockyProxyKill(DockyProxySub):
    """Kill your docky proxy"""

    def _main(self, *args):
        if not self.container:
            logger.info('Container do not exist, skip')
        else:
            if self.container.status != 'exited':
                logger.info('Kill docky proxy')
                self.container.kill()
            logger.info('Remove docky container proxy')
            self.container.remove()
