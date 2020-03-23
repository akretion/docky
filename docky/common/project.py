# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import re
from compose.project import OneOffFilter
from compose.cli import command
from compose.config.errors import ComposeFileNotFound
from plumbum import local

from .api import logger


class Project(object):

    def __init__(self):
        try:
            self.project = command.project_from_options('.', {})
        except ComposeFileNotFound:
            print("No docker-compose found, create one with :")
            print('$ docky init')
            exit(-1)

        self.name = self.project.name
        self.loaded_config = None
        self.service = self._get_main_service(self.project)

    def _get_main_service(self, project):
        """main_service has docky.main.service defined in
        his label."""
        for service in project.services:
            labels = service.options.get('labels', {})
            # service.labels() do not contain docky.main.service
            # see also compose.service.merge_labels
            if labels.get('docky.main.service', False):
                return service.name

    def get_containers(self, service=None):
        kwargs = {'one_off': OneOffFilter.include}
        if service:
            kwargs['service_names'] = [service]
        return self.project.containers(**kwargs)

    def display_service_tooltip(self):
        infos = self._get_services_info()
        for service in self.project.services:
            labels = service.options.get('labels', {})
            if labels.get('docky.access.help'):
                # TODO remove after some versions
                logger.warning(
                    "'docky.access.help' is replaced by 'docky.help'. "
                    "Please update this key in your docker files.")
            if infos.get(service.name):
                # some applications provide extra parameters to access resource
                infos[service.name] += labels.get("docky.url_suffix", "")
                logger.info(infos[service.name])
            if labels.get('docky.help'):
                logger.info(labels.get('docky.help'))

    def _get_services_info(self):
        """ Docker inspect provides all we need to guess ip of docky services
            Here is a format to retrieve information with
            a dedicated separator in this format:

            mystring:  as start separator
            :mystring  as end separator
        """
        format_ = "docker inspect --format='name: {{.Name}} :name - " \
                  "{{range $ip, $_ := .NetworkSettings.Networks}}" \
                  "ip: {{.IPAddress}}{{$ip}} :ip " \
                  "{{end}}:{{range $p, $conf := .Config.ExposedPorts}} " \
                  "port: {{$p}} :port {{end}} :port' $(docker ps -aq)"
        inspect = os.popen(format_)
        data, project_services = [], {}
        data = inspect.read()
        for info in data.split("\n"):
            if self.project.name in info:
                name, url = self._build_service_url(info)
                if name != "db":
                    project_services[name] = url
        return project_services

    def _build_service_url(self, origin):
        """ We extract informations from one line of docker inspect
            origin example
            name: /myproject_mailcatcher_1 :name - ip: 172.18.0.2myproject_local :ip :
             port: 1025/tcp :port  port: 1080/tcp :port  :port'
        """
        key_search = {
            "name": "/%s_(.*)_[0-9]{1,2}" % self.project.name,
            "ip": "(.*)%s_local" % self.project.name,
            "port": "([0-9]*)/tcp",
        }
        infos = {}
        for key, search in key_search.items():
            map_ = {"key": key, "search": search}
            match = re.match(r".*%(key)s: %(search)s :%(key)s" % map_, origin)
            if match and match.group(1):
                # we only get the first occurence
                infos[key] = match.group(1)
            else:
                infos[key] = ""
        url = "%(name)s http://%(ip)s:%(port)s" % infos
        return (infos.get("name"), url)

    def create_volume(self):
        """Mkdir volumes if they don't exist yet.

        Only apply to external volumes.
        docker-compose up do not attemps to create it
        so we have to do it ourselves"""
        for service in self.project.services:
            for volume in service.options.get('volumes', []):
                if volume.external:
                    path = local.path(local.env.expand(volume.external))
                    if not path.exists():
                        logger.info(
                            "Create missing directory %s for service %s",
                            path, service.name)
                        path.mkdir()

    def get_user(self, service_name):
        service = self.project.get_service(name=service_name)
        labels = service.options.get('labels')
        if labels:
            return labels.get('docky.user', None)
