#!/usr/bin/env python
# coding: utf-8

from plumbum import cli, local
from plumbum.cmd import git, docker, grep, sed
from plumbum.commands.modifiers import FG, TF, BG
from plumbum.cli.terminal import choose
import logging
import os
from compose.cli.command import get_project
from compose.project import OneOffFilter
from compose.parallel import parallel_kill
import yaml

compose = local['docker-compose']


DEFAULT_CONF = {
    "shared_eggs": True,
    "odoo": "https://github.com/oca/ocb.git",
    "template": "https://github.com/akretion/voodoo-template.git",
}

DEV_DOCKER_COMPOSE_FILENAME = 'dev.docker-compose.yml'

ODOO_DEV_DOCKER_COMPOSE_CONFIG = """
version: '2'

services:
  odoo:
    extends:
       file: docker-compose.yml
       service: odoo
    environment:
    - POSTGRESQL_DATA=/workspace/.db
    - POSTGRESQL_DB=db
    links:
    - db
    - mailcatcher
    ports:
    - 8069:8069
    - 8072:8072
    volumes:
    - .:/workspace
  mailcatcher:
    image: akretion/lightweight-mailcatcher
    ports:
    - 1080:1080
    - 1025:1025
  db:
    image: postgres:9.5
    environment:
    - POSTGRES_PASSWORD='odoo'
    - POSTGRES_USER='odoo'
    - POSTGRES_DB='db'
    volumes:
    - .db:/var/lib/postgresql/data
"""


class Voodoo(cli.Application):
    PROGNAME = "voodoo"
    VERSION = "1.0"

    dryrunFlag = cli.Flag(["dry-run"], help="Dry run mode")

    def _exec(self, cmd, retcode=FG):
	"""Log cmd before exec."""
	logging.info(cmd)
	if (self.dryrunFlag):
	    print cmd
	    return True
	return cmd & retcode

    def _get_home(self):
        return os.path.expanduser("~")

    def __init__(self, executable):
        super(Voodoo, self).__init__(executable)
        self.home = self._get_home()
        self.shared_folder = os.path.join(self.home, '.voodoo', 'shared')
        config_path = os.path.join(self.home, '.voodoo', 'config.yml')

        # Read existing configuration
        if os.path.isfile(config_path):
            config_file = open(config_path, 'r')
            config = yaml.safe_load(config_file)
        else:
            config = {}

        # Update configuration with default value and remove dead key
        new_config = DEFAULT_CONF.copy()
        for key, value in config.items():
            if key in DEFAULT_CONF:
                new_config[key] = config[key]
                # Set Configuration
                setattr(self, key, config[key])

        # Update config file if needed
        if new_config != config:
            logging.info("The Voodoo Configuration have been updated, "
                         "please take a look to the new config file")
            if not os.path.exists(self.shared_folder):
                os.makedirs(self.shared_folder)
            config_file = open(config_path, 'w')
            config_file.write(yaml.dump(new_config, default_flow_style=False))
            logging.info("Update default config file at %s" % config_path)

    @cli.switch("--verbose", help="Verbose mode")
    def set_log_level(self):
        logging.root.setLevel(logging.INFO)
        logging.info('Verbose mode activated')


class VoodooSub(cli.Application):

    def _exec(self, *args, **kwargs):
        self.parent._exec(*args, **kwargs)

    def _generate_dev_dockerfile(self):
        dc_file = open('docker-compose.yml', 'r')
        config = yaml.safe_load(dc_file)
        if 'odoo' in config['services']:
            template = ODOO_DEV_DOCKER_COMPOSE_CONFIG
        else:
            raise NotImplemented
        config = yaml.safe_load(template)
        dc_tmp_file = open('dev.docker-compose.yml', 'w')
        # share .voodoo folder in voodoo
        home = os.path.expanduser("~")
        shared = os.path.join(home, '.voodoo', 'shared')
        config['services']['odoo']['volumes'].append(
            '%s:%s' % (shared, shared))
        dc_tmp_file.write(yaml.dump(config, default_flow_style=False))

    def __init__(self, *args, **kwargs):
        super(VoodooSub, self).__init__(*args, **kwargs)
        if not os.path.exists(DEV_DOCKER_COMPOSE_FILENAME):
            self._generate_dev_dockerfile()
        self.compose = compose['-f', DEV_DOCKER_COMPOSE_FILENAME]

@Voodoo.subcommand("run")
class VoodooRun(VoodooSub):

    def _get_odoo_cache_path(self):
        cache_path = os.path.join(self.parent.shared_folder, 'cached_odoo')
        if not os.path.exists(cache_path):
            os.makedirs(cache_path)
        odoo_cache_path = os.path.join(cache_path, 'odoo')
        if not os.path.exists(odoo_cache_path):
            logging.info(
                "First run of Voodoo; there is no Odoo repo in %s! "
                "Will now download Odoo from Github, "
                "this can take a while...\n"
                "If you already have a local Odoo repo (from OCA) "
                "then you can you can abort the download "
                "and paste your repo or make a symbolink link in %s",
                odoo_ref_path, odoo_ref_path)
            self._exec(git["clone", self.parent.odoo, odoo_cache_path])
        else:
            print "Update Odoo cache"
            with local.cwd(odoo_cache_path):
                self._exec(git["pull"])
        return odoo_cache_path

    def _get_odoo(self, odoo_path):
        if not os.path.exists('parts'):
            os.makedirs('parts')
        odoo_cache_path = self._get_odoo_cache_path()
        self._exec(git["clone", "file://%s" % odoo_cache_path, odoo_path])

    def main(self, *args):
        odoo_path = os.path.join('parts', 'odoo')
        if not os.path.exists(odoo_path):
            self._get_odoo(odoo_path)
        # Remove useless dead container before running a new one
        self._exec(self.compose['rm', '--all', '-f'])
        self._exec(self.compose['run', 'odoo', 'bash'])


@Voodoo.subcommand("open")
class VoodooOpen(VoodooSub):

    def main(self, *args):
        project = get_project('.')
        container = project.containers(
            service_names=['odoo'], one_off=OneOffFilter.include)
        if container:
            self._exec(docker["exec", "-ti", container[0].name, "bash"])
        else:
            log.error("No container found for the service odoo "
                      "in the project %s" % project.name)


@Voodoo.subcommand("kill")
class VoodooKill(VoodooSub):

    def main(self, *args):
        # docker compose do not kill the container odoo as is was run
        # manually, so we implement our own kill
        project = get_project('.')
        containers = project.containers(one_off=OneOffFilter.include)
        parallel_kill(containers, {'signal': 'SIGKILL'})


@Voodoo.subcommand("new")
class VoodooNew(VoodooSub):

    def main(self, name):
        # TODO It will be better to use autocompletion
        # see plumbum and argcomplete
        # https://github.com/tomerfiliba/plumbum/blob/master/plumbum
        # /cli/application.py#L341
        # And https://github.com/kislyuk/argcomplete/issues/116
        self._exec(git["clone", self.parent.template, name])
        get_version = (
            git['branch', '-a']
            | grep['remote']
            | grep['-v', 'HEAD']
            | sed['s/remotes\/origin\///g'])
        versions = [v.strip() for v in get_version().split('\n')]
        versions.sort()
        version = choose(
            "Select your template?",
            versions,
            default = "9.0")
        with local.cwd(name):
            self._exec(git["checkout", version])


class VoodooForward(VoodooSub):
    _cmd = None

    def main(self, *args):
        return self._exec(self.compose[self._cmd])


@Voodoo.subcommand("build")
class VoodooBuild(VoodooForward):
    _cmd = "build"


@Voodoo.subcommand("start")
class VoodooStop(VoodooForward):
    _cmd = "start"


@Voodoo.subcommand("stop")
class VoodooStop(VoodooForward):
    _cmd = "stop"


@Voodoo.subcommand("ps")
class VoodooStop(VoodooForward):
    _cmd = "ps"


@Voodoo.subcommand("logs")
class VoodooLogs(VoodooForward):
    _cmd = "logs"


@Voodoo.subcommand("pull")
class VoodooLogs(VoodooForward):
    _cmd = "logs"


def main():
    Voodoo.run()

if __name__ == "__main__":
    Voodoo.run()
