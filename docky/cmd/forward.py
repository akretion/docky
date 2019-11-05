# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .base import Docky, DockySub


class DockyForward(DockySub):
    _cmd = None

    def _main(self, *args):
        cmd = self._cmd.split(' ')
        if args:
            cmd.append(*args)
        return self._run(self.compose[cmd])


@Docky.subcommand("build")
class DockyBuild(DockyForward):
    """Build or rebuild services"""
    _cmd = "build"


@Docky.subcommand("up")
class DockyUp(DockyForward):
    """Start all services in detached mode"""
    _cmd = "up -d"

    def _main(self, *args):
        self.project.display_service_tooltip()
        self.project.create_volume()
        return super(DockyUp, self)._main(*args)


@Docky.subcommand("down")
class DockyDown(DockyForward):
    """Stop all services"""
    _cmd = "down"


@Docky.subcommand("ps")
class DockyPs(DockyForward):
    """List containers"""
    _cmd = "ps"


@Docky.subcommand("logs")
class DockyLogs(DockyForward):
    """View output from containers"""
    _cmd = "logs -f --tail=100"


@Docky.subcommand("pull")
class DockyPull(DockyForward):
    """Pulls service images"""
    _cmd = "pull"


@Docky.subcommand("restart")
class DockyRestart(DockyForward):
    """Restart service"""
    _cmd = "restart"
