#!/usr/bin/env python
# coding: utf-8

from ..ruby.hook import RubyGenerateDevComposeFile, RubyInitRunDev


class RailsGenerateDevComposeFile(RubyGenerateDevComposeFile):
    _service = 'rails'


class RailsInitRunDev(RubyInitRunDev):
    _service = 'rails'
