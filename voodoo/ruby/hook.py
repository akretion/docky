#!/usr/bin/env python
# coding: utf-8

from ..hook import Deploy, InitRunDev, GenerateDevComposeFile, GetMainService
from plumbum.cli.terminal import choose
import os
import docker


class WagonGetMainService(GetMainService):
    _service = 'ruby'

    def run(self):
        if os.path.exists('Gemfile'):
            return 'ruby'

class OdooDeploy(Deploy):
        _service = 'ruby'


class WagonGenerateDevComposeFile(GenerateDevComposeFile):
    _service = 'ruby'

    def _update_config_file(self):
        super(WagonGenerateDevComposeFile, self)._update_config_file()
        networks = [net['Name'] for net in docker.Client().networks()]
        network = choose(
            "Select the network where your odoo is running",
            networks)
        self.config['networks'] = {
            'default': {'external': {'name': str(network)}}}


class WagonInitRunDev(InitRunDev):
    _service = 'ruby'

    def run(self):
        # Create shared bundle directory if not exist
        home = os.path.expanduser("~")
        bundle_path = os.path.join(home, '.voodoo', 'shared', 'bundle')
        if not os.path.exists(bundle_path):
            os.makedirs(bundle_path)

        # Init gems/bundle directory : share it or generate a new one
        if not os.path.exists('bundle'):
            if self.voodoo.parent.shared_gems:
                os.symlink(bundle_path, 'bundle')
            else:
                os.makedirs(os.path.join('bundle', 'bin'))
