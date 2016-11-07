#!/usr/bin/env python
# coding: utf-8

from ..hook import Deploy, GetMainService
from ..ruby.hook import RubyGenerateDevComposeFile, RubyInitRunDev
import os


class WagonGetMainService(GetMainService):
    _service = 'wagon'

    def run(self):
        if os.path.exists('Gemfile')\
                and 'wagon' in  open('Gemfile').read():
            return 'wagon'


class WagonDeploy(Deploy):
    _service = 'wagon'


class WagonGenerateDevComposeFile(RubyGenerateDevComposeFile):
    _service = 'wagon'


class WagonInitRunDev(RubyInitRunDev):
    _service = 'wagon'
