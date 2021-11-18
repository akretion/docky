#!/usr/bin/env python
# coding: utf-8

from plumbum.cmd import id, copier, ls
from plumbum.commands.modifiers import FG
from plumbum import local
from slugify import slugify

from ..common.api import logger

class GenerateProject(object):
    def _uid(self):
        return id['-u']().replace('\n', '')

    def _project_name(self):
        return slugify(local.cwd.name)
    
    def _is_copier_dir(self):
        return local.path(".copier-answers.yml").is_file()

    def _is_empty(self):
        # we don't care with dot files
        return len(ls()) == 0

    def generate(self, url, branch):
        if self._is_copier_dir():
            # if already inited ask the user with questions
            return copier['update'] & FG
        else:
            if not self._is_empty():
               raise BaseException("Not empty dir")
            return copier['-d', f'UID={self._uid()}', '-d', f'project_name={self._project_name()}', "-b", branch, url, '.'] & FG
        
