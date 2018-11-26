# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from plumbum import cli
from plumbum.cmd import git
from .base import Docky, DockySub, raise_error


@Docky.subcommand("migrate")
class DockyMigrate(DockySub):
    """TODO Migrate your odoo project"""
#
#    First you need to checkout the docky-upgrade template
#    available here : https://github.com/akretion/docky-upgrade
#    (It's a template a docky but based on open-upgrade'
#
#    Then go inside the repository clonned and launch the migration
#
#    * For migrating from 6.1 to 8.0 run:
#        docky migrate -b 7.0,8.0
#    * For migrating from 6.1 to 9.0 run:
#        docky migrate -b 7.0,8.0,9.0
#    * For migrating and loading a database run:
#        docky migrate -b 7.0,8.0 --db-file=tomigrate.dump
#
#    """

    db_file = cli.SwitchAttr(["db-file"])
    apply_branch = cli.SwitchAttr(
        ["b", "branch"],
        help="Branch to apply split by comma ex: 7.0,8.0",
        mandatory=True)
    _logs = []

    def log(self, message):
        print(message)
        self._logs.append(message)

    def _run_ak(self, *params):
        start = datetime.now()
        cmd = "ak " + " ".join(params)
        self.log("Launch %s" % cmd)
        self.compose("run", "odoo", "ak", *params)
        end = datetime.now()
        self.log("Run %s in %s" % (cmd, end-start))

    def _main(self):
        if self.main_service != 'odoo':
            raise_error("This command is used only for migrating odoo project")
        versions = self.apply_branch.split(',')
        logs = ["\n\nMigration Log Summary:\n"]
        first = True
        for version in versions:
            start = datetime.now()
            self._run(git["checkout", version])
            self._run_ak("build")
            if self.db_file and first:
                self._run_ak("db", "load", "--force", self.db_file)
                first = False
            self._run_ak("upgrade")
            self._run_ak("db", "dump", "--force", "migrated_%s.dump" % version)
            end = datetime.now()
            self.log("Migrate to version %s in %s" % (version, end-start))
        for log in self._logs:
            logger.info(log)
