# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import yaml
from .generator import GenerateComposeFile
from .api import logger


DEFAULT_CONF = {
    "verbose": True,
    "env": "dev",
    "network": {
        "name": "dy",
        "subnet": "172.30.0.0/16",
        "options": {
            "com.docker.network.bridge.name": "dy",
            "com.docker.network.bridge.host_binding_ipv4": "127.0.0.1",
        },
    },
    "proxy": {
        "custom_image": None,
        "name": "proxy-docky",
        "autostart": True,
    }
}


# TODO refactor code using local object of plumbum instead of os
class DockyConfig(object):

    def _get_home(self):
        return os.path.expanduser("~")

    def __init__(self):
        super(DockyConfig, self).__init__()
        self.home = self._get_home()
        docky_folder = os.path.join(self.home, '.docky')
        if not os.path.exists(docky_folder):
            os.makedirs(docky_folder)
        self.config_path = os.path.join(self.home, '.docky', 'config.yml')
        current_config = self._get_config()
        config = self._get_config_with_default_value(current_config)

        if current_config != config:
            self._update_config_file(config)
        self.env = config['env']
        self.verbose = config['verbose']
        self.network = config['network']
        self.proxy = config['proxy']

    def _get_config(self):
        if os.path.isfile(self.config_path):
            return yaml.safe_load(open(self.config_path, 'r'))
        else:
            return {}

    def _get_config_with_default_value(self, current_config):
        config = DEFAULT_CONF.copy()
        for key, value in DEFAULT_CONF.items():
            if key in current_config:
                config[key] = current_config[key]
        return config

    def _update_config_file(self, config):
        logger.info("The Docky Configuration have been updated, "
                    "please take a look to the new config file")
        config_file = open(self.config_path, 'w')
        config_file.write(yaml.dump(config, default_flow_style=False))
        logger.info("Update default config file at %s", self.config_path)
