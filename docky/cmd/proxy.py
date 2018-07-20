# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .base import Docky, DockySub, raise_error, logger


@Docky.subcommand("proxy")
class DockyProxy(DockySub):
    """Start/Restart/Stop your docky proxy"""

    def _main(self, *args):
        if not self.nested_command:
            raise_error("Please specify an action, start/stop/restart/kill/ps")


@DockyProxy.subcommand("start")
class DockyProxyStart(DockySub):
    """Start your docky proxy"""

    def _main(self, *args):
        self.proxy.start()


@DockyProxy.subcommand("stop")
class DockyProxyStop(DockySub):
    """Stop your docky proxy"""

    def _main(self, *args):
        self.proxy.stop()


@DockyProxy.subcommand("restart")
class DockyProxyRestart(DockySub):
    """Restart your docky proxy"""

    def _main(self, *args):
        self.proxy.restart()


@DockyProxy.subcommand("ps")
class DockyProxyPs(DockySub):
    """Get the status of your docky proxy"""

    def _main(self, *args):
        self.proxy.status()


@DockyProxy.subcommand("kill")
class DockyProxyKill(DockySub):
    """Kill your docky proxy"""

    def _main(self, *args):
        self.proxy.kill()
