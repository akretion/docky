# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import docker
from .api import logger

client = docker.from_env()

DOCKY_PROXY_DEFAULT_IMAGE = "quay.io/akretion/docky-proxy:20180723"


class Proxy(object):

    def __init__(self, docky_config):
        super(Proxy, self).__init__()
        self.network = docky_config.network
        config = docky_config.proxy
        self.image = config.get('custom_image') or DOCKY_PROXY_DEFAULT_IMAGE
        self.name = config['name']
        self.autostart = config['autostart']
        self.container = self._get_container()

    def _get_container(self):
        container = client.containers.list(
            all=True,
            filters={'name': self.name})
        return container[0] if container else None

    def _restart(self):
        logger.info("Restart docky proxy")
        self.container.restart()

    def _start(self):
        logger.info("Start Docky proxy")
        client.containers.run(
            self.image,
            hostname=self.name,
            name=self.name,
            network_mode=self.network['name'],
            volumes=[
                "/var/run/docker.sock:/tmp/docker.sock:ro",
                ],
                detach=True)

    def start_if_needed(self):
        if self.autostart and not self._is_running():
            self.start()

    def _is_running(self):
        return self.container and self.container.status == 'running'

    def start(self):
        if not self.container:
            self._start()
        elif self.container.status != 'running':
            logger.info(
                "A container already exist but is not running. Restart it")
            self._restart()
        else:
            logger.info("Proxy is already running, skip")

    def stop(self):
        if not self._is_running():
            logger.info("Proxy is already stopped, skip")
        else:
            logger.info("Stop the Proxy")
            self.container.stop()

    def restart(self):
        if not self.container:
            logger.info("There is no proxy start it")
            self._start()
        else:
            self._restart()

    def status(self):
        if self.container:
            status = self.container.status
        else:
            status = 'container do not exist'
        logger.info('Proxy status: %s', status)

    def kill(self):
        if not self.container:
            logger.info('Container do not exist, skip')
        else:
            if self.container.status != 'exited':
                logger.info('Kill docky proxy')
                self.container.kill()
            logger.info('Remove docky container proxy')
            self.container.remove()
