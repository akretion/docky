# Copyright 2022 Akretion (https://www.akretion.com).
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import os
from plumbum.cli.terminal import ask, prompt


TELEPORT_PROXY = "teleport.akretion.com:443"

class RemoteVM(object):

    def __init__(self, name):
        super().__init__()
        self.name = name

    def _remote_exec(self, command):
        remote_command = f"tsh --proxy={TELEPORT_PROXY} ssh app@{self.name} bash -c '{command}'"
        output = os.popen(remote_command).readlines()
        echo(output)
        return

    def clone(self, project_url, project_access_token, dir_name):
        project_url_with_token = project_url.replace("https://", f"https://oauth2:{project_access_token}@")
        self._remote_exec(f"git clone {project_url_with_token} {dir_name}")
