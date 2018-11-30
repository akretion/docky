# coding: utf-8
from compose import cli
from compose.service import Service
from compose.cli.main import TopLevelCommand
from compose.const import LABEL_CONTAINER_NUMBER


# This is a patched version of docker-compose
# We patch it in order to be able to
# - do a docker-compose exec on a running container (launch with run)


get_ori_container = Service.get_container


def get_run_container(self, number=1):
    # search for container running in background
    for container in self.containers(
            labels=['{0}={1}'.format(LABEL_CONTAINER_NUMBER, number)]):
        return container

    # search for container running with "run" cmd
    for container in self.containers(one_off=True):
        if container.service == self.name:
            return container
    raise ValueError("No container found for %s_%s" % (self.name, number))


def main():
    Service.get_container = get_run_container
    cli.main.main()
