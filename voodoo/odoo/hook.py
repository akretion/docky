#!/usr/bin/env python
# coding: utf-8

from ..hook import Deploy, InitRunDev, GenerateDevComposeFile, GetMainService
from plumbum import local
from plumbum.cmd import git

import os


class OdooGetMainService(GetMainService):
    _service = 'odoo'

    def run(self):
        if os.path.exists('buildout.cfg'):
            return 'odoo'
        return None


class OdooDeploy(Deploy):
    _service = 'odoo'

    def _build(self):
        buildout_file = "%s.buildout.cfg" % self.voodoo.env
        if not os.path.isfile(buildout_file):
            print (
                "The %s is missing, please add one before deploying"
                % buildout_file)
        return super(OdooDeploy, self)._build()

    def _update_application(self):
        self._run(self._compose['run', '--rm', 'odoo', 'ak', 'upgrade'])


class GenerateDevComposeFile(GenerateDevComposeFile):
    _service = 'odoo'
    _map_user_for_service = ['db']

    def get_default_volume(self):
        path = local.path('~/.voodoo/shared')._path
        return [':'.join([path, path])]

    def _update_config_file(self):
        super(GenerateDevComposeFile, self)._update_config_file()
        path = local.path('~/.voodoo/shared/maintainer_quality_tools')._path
        self.config['services']['odoo']['environment'].append(
            "MAINTAINER_QUALITY_TOOLS=%s" % path)


class OdooInitRunDev(InitRunDev):
    _service = 'odoo'

    def _get_odoo_cache_path(self):
        cache_path = os.path.join(self.voodoo.parent.shared_folder, 'cached_odoo')
        if not os.path.exists(cache_path):
            os.makedirs(cache_path)
        odoo_cache_path = os.path.join(cache_path, 'odoo')
        if not os.path.exists(odoo_cache_path):
            print (
                "First run of Voodoo; there is no Odoo repo in %s! \n"
                "Will now download Odoo from Github, "
                "this can take a while...\n"
                "If you already have a local Odoo repo (from OCA) "
                "then you can you can abort the download "
                "and paste your repo or make a symbolink link in %s"
                % (odoo_cache_path, odoo_cache_path))
            self._run(git["clone", self.voodoo.parent.odoo, odoo_cache_path])
        else:
            print "Updating Odoo cache..."
            with local.cwd(odoo_cache_path):
                self._run(git["pull"])
        return odoo_cache_path

    def _get_odoo(self, odoo_path):
        if not os.path.exists('parts'):
            os.makedirs('parts')
        odoo_cache_path = self._get_odoo_cache_path()
        self._run(git["clone", "file://%s" % odoo_cache_path, odoo_path])

    def _copy_eggs_directory(self, dest):
        self._run(self._compose[
            'run', 'odoo', 'cp', '-r', '/opt/voodoo/eggs', dest])

    def _get_maintainer_quality_tools_path(self):
        path = local.path(
            "%s/maintainer_quality_tools"
            % self.voodoo.parent.shared_folder)
        if not path.is_dir():
            print (
                "First run of Voodoo; there is no Maintainer Quality Tools "
                "repo in %s! \nWill now download it from Github, "
                "this can take a while...\n"
                % (path._path))
            self._run(git["clone",
                          self.voodoo.parent.maintainer_quality_tools,
                          path._path])

    def run(self):
        # create db directory data and socket if missing
        for directory in ['socket', 'data']:
            path = os.path.join('.db', directory)
            if not os.path.exists(path):
                os.makedirs(path)

        # Create maintainer quality tools
        self._get_maintainer_quality_tools_path()

        # Create odoo directory from cache if do not exist
        odoo_path = os.path.join('parts', 'odoo')
        if not os.path.exists(odoo_path):
            self._get_odoo(odoo_path)

        # Create shared eggs directory if not exist
        home = os.path.expanduser("~")
        eggs_path = os.path.join(home, '.voodoo', 'shared', 'eggs')
        if not os.path.exists(eggs_path):
            self._copy_eggs_directory(eggs_path)

        # Init eggs directory : share it or generate a new one
        if not os.path.exists('eggs'):
            if self.voodoo.parent.shared_eggs:
                os.symlink(eggs_path, 'eggs')
            else:
                self._copy_eggs_directory(eggs_path)
