#!/usr/bin/env python
# coding: utf-8

from ..ruby.hook import RubyGenerateDevComposeFile, RubyInitRunDev


class WagonGenerateDevComposeFile(RubyGenerateDevComposeFile):
    _service = 'wagon'


class WagonInitRunDev(RubyInitRunDev):
    _service = 'wagon'
