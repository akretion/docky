#!/usr/bin/env python
# coding: utf-8

from ..hook import Deploy, GetMainService
from ..ruby.hook import RubyGenerateDevComposeFile, RubyInitRunDev
import os


class RailsGetMainService(GetMainService):
    _service = 'rails'

    def run(self):
        if os.path.exists('Gemfile')\
                and 'rails' in  open('Gemfile').read():
            return 'rails'


class RailsDeploy(Deploy):
    _service = 'rails'


class RailsGenerateDevComposeFile(RubyGenerateDevComposeFile):
    _service = 'rails'


class RailsInitRunDev(RubyInitRunDev):
    _service = 'rails'
