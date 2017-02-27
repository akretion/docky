#!/usr/bin/env python
# coding: utf-8

from ..hook import InitRunDev, GenerateDevComposeFile
from plumbum.cli.terminal import choose
from plumbum import local
import docker


class RubyGenerateDevComposeFile(GenerateDevComposeFile):
    _service = 'ruby'

    def get_default_volume(self):
        path = local.path('~/.voodoo/shared/bundle')._path
        return [':'.join([path, '/usr/local/bundle'])]


class RubyInitRunDev(InitRunDev):
    _service = 'ruby'

    def run(self):
        # Create shared bundle directory if not exist
        local.path('~/.voodoo/shared/bundle').mkdir()
