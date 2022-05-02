# Copyright 2022 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import os
from plumbum import cli
from plumbum.cli.terminal import ask, prompt

from .base import Docky

from ..common.remote import RemoteVM
from ..common.gitlab import Gitlab


@Docky.subcommand("remote")
class DockyRemote(cli.Application):
    """Handle remote env"""

@DockyRemote.subcommand("init")
class DockyRemote(cli.Application):
    """Init remote repository"""

    def main(self, *args, **kwargs):
        project_url = os.popen("git remote get-url origin").readline()
        project_url = project_url.replace("\n", "")
        project_url = project_url.replace("ssh://git@", "https://")
        project_url = project_url.replace(":10022/", "/")
        project_url = project_url.replace(".git", "")
        project_name = project_url.rsplit("/")[-1]
        vm_name = prompt(
            "What is the name of the VM ?", default=project_name)
        project_access_token = prompt(
                f"\n\n{project_url}/-/settings/access_tokens\n"\
                "Please create the Project Access Token\n"\
                "Then paste it here (read_repository & read_registry needed)")
        dir_name = prompt(
            "In which directory do you want to clone the project in the VM ?", default=project_name)
        RemoteVM(vm_name).clone(project_url, project_access_token, dir_name)
