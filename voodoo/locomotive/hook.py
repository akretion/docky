#!/usr/bin/env python
# coding: utf-8

from ..hook import Deploy, GetMainService
from ..ruby.hook import RubyGenerateDevComposeFile, RubyInitRunDev
import os


class LocoGetMainService(GetMainService):
    _service = 'locomotive'

    def run(self):
        if os.path.exists('Gemfile')\
                and 'locomotivecms' in  open('Gemfile').read():
            return 'locomotive'


class LocoDeploy(Deploy):
    _service = 'locomotive'


class LocoGenerateDevComposeFile(RubyGenerateDevComposeFile):
    _service = 'locomotive'


class LocoInitRunDev(RubyInitRunDev):
    _service = 'locomotive'
