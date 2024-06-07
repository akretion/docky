# Copyright 2018-TODAY Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from python_on_whales import docker
from plumbum import local

from .api import logger


class Project(object):

    def __init__(self):
        try:
            self.project = docker.compose.config(return_json=True)
        except:
            print("No docker-compose found, create one with :")
            print("$ docky init")
            exit(-1)

        self.name = self.project.get("name")
        self.loaded_config = self.project
        self.service = self._get_main_service(self.project)

    def _get_main_service(self, project):
        """main_service has docky.main.service defined in
        his label."""
        for service in project.get("services"):
            labels = project["services"][service].get("labels")
            # service.labels() do not contain docky.main.service
            # see also compose.service.merge_labels
            if labels:
                if labels.get("docky.main.service"):
                    return service

    def get_containers(self, service=None):
        kwargs = {}
        if service:
            kwargs["services"] = [service]
        return docker.compose.ps(**kwargs)

    def display_service_tooltip(self):
        infos = self._get_services_info()
        for service in self.project.get("services"):
            dict_service = self.project["services"].get(service)
            labels = dict_service.get("labels", {})
            if labels.get("docky.access.help"):
                # TODO remove after some versions
                logger.warning(
                    "'docky.access.help' is replaced by 'docky.help'. "
                    "Please update this key in your docker files.")
            if infos.get(dict_service.get("name")):
                # some applications provide extra parameters to access resource
                infos[service.name] += labels.get("docky.url_suffix", "")
                logger.info(infos[service.name])
            if labels.get("docky.help"):
                logger.info(labels.get("docky.help"))

    def _get_services_info(self):
        """ Search IP and Port for each services
        """
        infos = {}
        main_service = self._get_main_service(self.project)
        for service in self.project.get("services"):
            if service != main_service:
                continue
            serv = self.project["services"][service]
            proj_key = [
                x for x in serv["networks"].keys()]
            proj_key = proj_key and proj_key[0] or False
            if not serv["networks"]:
                continue
            ip = serv["networks"].get("IPAdress", "")
            info = {
                "name": serv["labels"].get(
                    "com.docker.compose.service", ""),
                "ip": ip,
                "port": [x for x in serv.get("ports", "")],
            }
            if info["name"] != "db" and info.get("port"):
                urls = ["http://%s:%s" % (info["ip"], port.replace("/tcp", ""))
                        for port in info["port"][0]]
                # There is no web app to access 'db' service: try adminer for that
                infos[info["name"]] = "%s %s" % (info["name"], " ".join(urls))
        return infos

    def create_volume(self):
        """Mkdir volumes if they don't exist yet.

        Only apply to external volumes.
        docker-compose up do not attemps to create it
        so we have to do it ourselves"""
        for service in self.project.get("services"):
            dict_service = self.project["services"].get(service)
            for volume in dict_service.get("volumes", []):
                if volume.get("external"):
                    path = local.path(local.env.expand(volume.external))
                    if not path.exists():
                        logger.info(
                            "Create missing directory %s for service %s",
                            path, service.name)
                        path.mkdir()

    def get_user(self, service_name):
        labels = self.project["services"].get(service_name).get("labels")
        if labels:
            return labels.get("docky.user")
