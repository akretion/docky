#!/usr/bin/env python
# coding: utf-8

from ..hook import InitRunDev


class WagonInitRunDev(InitRunDev):
    _service = 'odoo'

    def run(self):
        # Create shared eggs directory if not exist
        home = os.path.expanduser("~")
        bundle_path = os.path.join(home, '.voodoo', 'shared', 'bundle')
        if not os.path.exists(bundle_path):
            os.makedirs(bundle_path)

        # Init gems/bundle directory : share it or generate a new one
        if not os.path.exists('bundle'):
            if self.parent.shared_gems:
                os.symlink(bundle_path, 'bundle')
            else:
                os.makedirs(os.path.join('bundle', 'bin'))

