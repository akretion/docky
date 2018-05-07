#!/usr/bin/env python
# coding: utf-8

from ..hook import InitRunDev, GenerateDevComposeFile
from plumbum import local
from plumbum.cmd import git

import os


class GenerateDevComposeFile(GenerateDevComposeFile):
    _service = 'odoo'
    _map_user_for_service = ['db']

    def get_default_volume(self):
        path = '/home/${USER}/.docky/shared'
        return [':'.join([path, path])]

    def _update_config_file(self):
        super(GenerateDevComposeFile, self)._update_config_file()
        path = '/home/${USER}/.docky/shared/maintainer_quality_tools'
        self.config['services']['odoo']['environment'].append(
            "MAINTAINER_QUALITY_TOOLS=%s" % path)


class OdooInitRunDev(InitRunDev):
    _service = 'odoo'

    # TODO maybe move this in AK
    def _get_maintainer_quality_tools_path(self):
        path = local.path(
            "%s/maintainer_quality_tools"
            % self.docky.parent.shared_folder)
        if not path.is_dir():
            print (
                "First run of Docky; there is no Maintainer Quality Tools "
                "repo in %s! \nWill now download it from Github, "
                "this can take a while...\n"
                % (path._path))
            self._run(git["clone",
                          self.docky.parent.maintainer_quality_tools,
                          path._path])

    def run(self):
        # create db directory data and socket if missing
        for directory in ['socket', 'data']:
            path = os.path.join('.db', directory)
            if not os.path.exists(path):
                os.makedirs(path)

        # Create maintainer quality tools
        self._get_maintainer_quality_tools_path()
