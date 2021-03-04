# -*- coding: utf-8 -*-
# Copyright 2019 Akretion (http://www.akretion.com).
# @author Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from plumbum import cli
from plumbum.cli.terminal import ask


from .base import Docky
from ..common.generator import GenerateProject


@Docky.subcommand("init")
class DockyInit(cli.Application):
    """Initalize a project"""
    TEMPLATE_URL = "https://github.com/akretion/docky-odoo-template.git"
    TEMPLATE_BRANCH = "14.0"
    template_branch = cli.SwitchAttr("--b", help="Template's branch", argtype=str, default=TEMPLATE_BRANCH)
    template_url = cli.SwitchAttr("--url", help="Template's url", argtype=str, default=TEMPLATE_URL)
    
    def main(self, *args, **kwargs):
        GenerateProject().generate(url=self.template_url, branch=self.template_branch)
