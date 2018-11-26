# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .base import Docky, DockySubNoProject, raise_error, logger
from plumbum import cli


@Docky.subcommand("proxy")
class DockyProxy(cli.Application):
    """Start/Restart/Stop your docky proxy"""

    def main(self, *args, **kwargs):
        self.force_env = self.parent.force_env
        self.env = self.parent.config.env
        self.config = self.parent.config
        if not self.nested_command:
            raise_error("Please specify an action, start/stop/restart/kill/ps")

@DockyProxy.subcommand("start")
class DockyProxyStart(DockySubNoProject):
    """Start your docky proxy"""

    def _main(self, *args):
        self.proxy.start()


@DockyProxy.subcommand("stop")
class DockyProxyStop(DockySubNoProject):
    """Stop your docky proxy"""

    def _main(self, *args):
        self.proxy.stop()


@DockyProxy.subcommand("restart")
class DockyProxyRestart(DockySubNoProject):
    """Restart your docky proxy"""

    def _main(self, *args):
        self.proxy.restart()


@DockyProxy.subcommand("ps")
class DockyProxyPs(DockySubNoProject):
    """Get the status of your docky proxy"""

    def _main(self, *args):
        self.proxy.status()


@DockyProxy.subcommand("kill")
class DockyProxyKill(DockySubNoProject):
    """Kill your docky proxy"""

    def _main(self, *args):
        self.proxy.kill()
