# Copyright 2022 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import os
from plumbum.cli.terminal import ask, prompt
from plumbum.cmd import tsh

from ..common.api import logger


TELEPORT_PROXY = "teleport.akretion.com:443"

class RemoteVM(object):

    def __init__(self, name):
        super().__init__()
        self.name = name

    def _remote_exec(self, command):
        remote_command = tsh["--proxy", TELEPORT_PROXY, "ssh", f"app@{self.name}", "bash", "-c", f"'{command}'"]
        logger.info(str(remote_command))
        return remote_command()

    def clone(self, project_url, project_access_token, dir_name):
        project_url_with_token = project_url.replace("https://", f"https://oauth2:{project_access_token}@")
        self._remote_exec(f"git clone {project_url_with_token} {dir_name}")
