# Copyright 2022 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import yaml
from plumbum import cli
from plumbum.cmd import echo, tsh

from .base import Docky, DockySubNoProject


TELEPORT_PROXY = "teleport.akretion.com:443"


@Docky.subcommand("remote")
class DockyRemote(DockySubNoProject):

    def _main(self, *args):
        pass


class DockyRemoteSub(cli.Application):
    """Handle remote env"""
    _cmd = None

    def _run(self, *args, **kwargs):
        self.parent._run(*args, **kwargs)

    def _init_remote(self):
        with cli.Config(".deploy.conf") as conf:
            self.vm_name = conf.get("default.vm")
            self.dir_name = conf.get("default.dir")
            self.repo_url = conf.get("default.repo_url")
            repo_access_token = conf.get("default.repo_access_token")
            self.repo_url_with_token = self.repo_url.replace("https://", f"https://oauth2:{repo_access_token}@")
        if self._cmd:
            self._cmd = f"cd {self.dir_name} && docker-compose " + self._cmd

    def main(self, *args, **kwargs):
        self._init_remote()
        self._main(*args, **kwargs)

    def _main(self, *args):
        cmd = ["--proxy", TELEPORT_PROXY, "ssh", f"app@{self.vm_name}", "bash", "-c"]
        cmd.append(f"'{self._cmd}'")
        return self._run(tsh[cmd])


@DockyRemote.subcommand("clone")
class DockyRemoteClone(DockyRemoteSub):
    """Clone remote repository"""

    def _init_remote(self):
        super()._init_remote()
        self._cmd = f"git clone {self.repo_url_with_token} {self.dir_name}"

@DockyRemote.subcommand("pull")
class DockyRemotePull(DockyRemoteSub):
    """Pull docker images"""
    _cmd = "pull"

@DockyRemote.subcommand("up")
class DockyRemoteUp(DockyRemoteSub):
    """make remote project up"""
    _cmd = "up -d"

@DockyRemote.subcommand("down")
class DockyRemoteUp(DockyRemoteSub):
    """make remote project down"""
    _cmd = "down"

@DockyRemote.subcommand("logs")
class DockyRemoteLogs(DockyRemoteSub):
    """View output from remote containers"""
    _cmd = "logs -f --tail=100"

@DockyRemote.subcommand("restart")
class DockyRemoteRestart(DockyRemoteSub):
    """Restart remote service"""
    _cmd = "restart"
