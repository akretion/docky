# Copyright 2018-TODAY Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from .base import Docky, DockySub


@Docky.subcommand("kill")
class DockyKill(DockySub):
    """Kill all running container of the project"""

    def _main(self, *args):
        # docker compose do not kill the container odoo as is was run
        # manually, so we implement our own kill
        self._run(self.compose["kill", "-s", "SIGKILL"])
