#!/usr/bin/env python
# coding: utf-8

from ..hook import InitRunDev, GenerateDevComposeFile
from plumbum.cli.terminal import choose
from plumbum import local
import docker


class RubyGenerateDevComposeFile(GenerateDevComposeFile):
    _service = 'ruby'

    def _update_config_file(self):
        super(RubyGenerateDevComposeFile, self)._update_config_file()
        networks = [net['Name'] for net in docker.Client().networks()]
        network = choose(
            "Select the network where your odoo is running",
            networks)
        self.config['networks'] = {
            'default': {'external': {'name': str(network)}}}

    def get_default_volume(self):
        path = local.path('~/.voodoo/shared/bundle')._path
        return [':'.join([path, '/usr/local/bundle'])]


class RubyInitRunDev(InitRunDev):
    _service = 'ruby'

    def run(self):
        # Create shared bundle directory if not exist
        local.path('~/.voodoo/shared/bundle').mkdir()
