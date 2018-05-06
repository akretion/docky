#!/usr/bin/env python
# coding: utf-8

from ..ruby.hook import RubyGenerateDevComposeFile, RubyInitRunDev


class LocoGenerateDevComposeFile(RubyGenerateDevComposeFile):
    _service = 'locomotive'


class LocoInitRunDev(RubyInitRunDev):
    _service = 'locomotive'
