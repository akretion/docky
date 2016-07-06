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
services:
  db:
    environment:
    - POSTGRES_PASSWORD=odoo
    - POSTGRES_USER=odoo
    - POSTGRES_DB=db
    image: akretion/voodoo-postgresql
    volumes:
    - .db:/var/lib/postgresql/data
    - .db/socket/:/var/run/postgresql/
  mailcatcher:
    image: akretion/lightweight-mailcatcher
    ports:
    - 1280:1080
    - 1225:1025
  odoo:
    environment:
    - PYTHONDONTWRITEBYTECODE=True
    extends:
      file: docker-compose.yml
      service: odoo
    links:
    - db
    - mailcatcher
    ports:
    - 8069:8069
    - 8072:8072
    volumes:
    - .:/workspace
    - .db/socket/:/var/run/postgresql/
version: '2'
"""


class Voodoo(cli.Application):
    PROGNAME = "voodoo"
    VERSION = "1.0"

    dryrun = cli.Flag(["dry-run"], help="Dry run mode")

    def _run(self, cmd, retcode=FG):
        """Run a command in a new process and log it"""
        logging.info(cmd)
        if (self.dryrun):
            print cmd
            return True
        return cmd & retcode

    def _exec(self, cmd, args=[]):
        """Run a command in the same process and log it
        this will replace the current process by the cmd"""
        logging.info([cmd, args])
        if (self.dryrun):
            print "os.execvpe (%s, %s, env)" % (cmd, [cmd] + args)
            return True
        os.execvpe(cmd, [cmd] + args, local.env)

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
            logging.warning("The Voodoo Configuration have been updated, "
                            "please take a look to the new config file")
            if not os.path.exists(self.shared_folder):
                os.makedirs(self.shared_folder)
            config_file = open(config_path, 'w')
            config_file.write(yaml.dump(new_config, default_flow_style=False))
            logging.warning("Update default config file at %s" % config_path)

    @cli.switch("--verbose", help="Verbose mode")
    def set_log_level(self):
        logging.root.setLevel(logging.INFO)
        logging.info('Verbose mode activated')


class VoodooSub(cli.Application):

    def _exec(self, *args, **kwargs):
        self.parent._exec(*args, **kwargs)

    def _run(self, *args, **kwargs):
        self.parent._run(*args, **kwargs)

    def _generate_odoo_dev_dockerfile(self):
        dc_file = open('docker-compose.yml', 'r')
        config = yaml.safe_load(dc_file)
        if 'odoo' in config['services']:
            template = ODOO_DEV_DOCKER_COMPOSE_CONFIG
        else:
            raise NotImplemented
        config = yaml.safe_load(template)
        with open('dev.docker-compose.yml', 'w') as dc_tmp_file:

            # share .voodoo folder in voodoo
            home = os.path.expanduser("~")
            shared = os.path.join(home, '.voodoo', 'shared')
            config['services']['odoo']['volumes'].append(
                '%s:%s' % (shared, shared))

            # inject uid for sharing db folder with host
            uid = os.getuid()
            for key in ['USERMAP_UID', 'USERMAP_GID']:
                config['services']['db']['environment'].append(
                    "%s=%s" % (key,uid))

            dc_tmp_file.write(yaml.dump(config, default_flow_style=False))

    def _get_main_service(self):
        dc_file = open('docker-compose.yml', 'r')
        config = yaml.safe_load(dc_file)
        for name, vals in config['services'].items():
            if vals.get('labels', {}).get('main_service') == "True":
                return name
        return None

    def __init__(self, *args, **kwargs):
        super(VoodooSub, self).__init__(*args, **kwargs)
        if args and args[0] == 'voodoo new':
            return
        self.main_service = self._get_main_service()
        if not os.path.exists(DEV_DOCKER_COMPOSE_FILENAME):
            if self.main_service == 'odoo':
                self._generate_odoo_dev_dockerfile()
        if os.path.isfile(DEV_DOCKER_COMPOSE_FILENAME):
            self.config_path = DEV_DOCKER_COMPOSE_FILENAME
        else:
            self.config_path = 'docker-compose.yml'
        self.compose = compose['-f', self.config_path]


@Voodoo.subcommand("run")
class VoodooRun(VoodooSub):
    """Start services and enter in your dev container"""

    def _get_odoo_cache_path(self):
        cache_path = os.path.join(self.parent.shared_folder, 'cached_odoo')
        if not os.path.exists(cache_path):
            os.makedirs(cache_path)
        odoo_cache_path = os.path.join(cache_path, 'odoo')
        if not os.path.exists(odoo_cache_path):
            print (
                "First run of Voodoo; there is no Odoo repo in %s! \n"
                "Will now download Odoo from Github, "
                "this can take a while...\n"
                "If you already have a local Odoo repo (from OCA) "
                "then you can you can abort the download "
                "and paste your repo or make a symbolink link in %s"
                % (odoo_cache_path, odoo_cache_path))
            self._run(git["clone", self.parent.odoo, odoo_cache_path])
        else:
            print "Update Odoo cache"
            with local.cwd(odoo_cache_path):
                self._run(git["pull"])
        return odoo_cache_path

    def _get_odoo(self, odoo_path):
        if not os.path.exists('parts'):
            os.makedirs('parts')
        odoo_cache_path = self._get_odoo_cache_path()
        self._run(git["clone", "file://%s" % odoo_cache_path, odoo_path])

    def _copy_eggs_directory(self, dest):
        self._run(self.compose[
            'run', 'odoo', 'cp', '-r', '/opt/voodoo/eggs', dest])

    def _init_odoo_run(self):
        # create db folder if missing
        if not os.path.exists('.db'):
            os.makedirs('.db')

        # create db socket folder if missing
        if not os.path.exists('.db/socket'):
            os.makedirs('.db/socket')

        # Create odoo directory from cache if do not exist
        odoo_path = os.path.join('parts', 'odoo')
        if not os.path.exists(odoo_path):
            self._get_odoo(odoo_path)

        # Create shared eggs directory if not exist
        home = os.path.expanduser("~")
        eggs_path = os.path.join(home, '.voodoo', 'shared', 'eggs')
        if not os.path.exists(eggs_path):
            self._copy_eggs_directory(eggs_path)

        # Init eggs directory : share it or generate a new one
        if not os.path.exists('eggs'):
            if self.parent.shared_eggs:
                os.symlink(eggs_path, 'eggs')
            else:
                self._copy_eggs_directory(eggs_path)

    def main(self, *args):
        service = self.main_service
        if service == 'odoo':
            self._init_odoo_run()
        # Remove useless dead container before running a new one
        self._run(self.compose['rm', '--all', '-f'])
        self._exec('docker-compose', [
            '-f', self.config_path,
            'run', '--service-ports',
            self.main_service, 'bash'])


@Voodoo.subcommand("open")
class VoodooOpen(VoodooSub):
    """Open a new session inside your dev container"""

    def main(self, *args):
        project = get_project('.', [self.config_path])
        container = project.containers(
            service_names=[self.main_service], one_off=OneOffFilter.include)
        if container:
            self._exec('docker',
                       ["exec", "-ti", container[0].name, "bash"])
        else:
            log.error("No container found for the service odoo "
                      "in the project %s" % project.name)


@Voodoo.subcommand("kill")
class VoodooKill(VoodooSub):
    """Kill all running container of the project"""

    def main(self, *args):
        # docker compose do not kill the container odoo as is was run
        # manually, so we implement our own kill
        project = get_project('.', config_path=[self.config_path])
        containers = project.containers(one_off=OneOffFilter.include)
        parallel_kill(containers, {'signal': 'SIGKILL'})


@Voodoo.subcommand("new")
class VoodooNew(VoodooSub):
    """Create a new project"""

    def main(self, name):
        # TODO It will be better to use autocompletion
        # see plumbum and argcomplete
        # https://github.com/tomerfiliba/plumbum/blob/master/plumbum
        # /cli/application.py#L341
        # And https://github.com/kislyuk/argcomplete/issues/116
        self._run(git["clone", self.parent.template, name])
        with local.cwd(name):
            get_version = (git['branch', '-a']
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
            self._run(git["checkout", version])


@Voodoo.subcommand("inspect")
class VoodooInspect(VoodooSub):
    """Simple Inspection of network will return ip and hostname"""

    def main(self):
        project = get_project('.', config_path=[self.config_path])
        network = project.networks.networks['default'].inspect()
        print "Network name : %s" % network['Name']
        for uid, container in network['Containers'].items():
            print "%s : %s" % (container['Name'], container['IPv4Address'])


class VoodooForward(VoodooSub):
    _cmd = None

    def main(self, *args):
        return self._run(self.compose[self._cmd])


@Voodoo.subcommand("build")
class VoodooBuild(VoodooForward):
    """Build or rebuild services"""
    _cmd = "build"


@Voodoo.subcommand("start")
class VoodooStart(VoodooForward):
    """Start services"""
    _cmd = "start"


@Voodoo.subcommand("stop")
class VoodooStop(VoodooForward):
    """Stop services"""
    _cmd = "stop"


@Voodoo.subcommand("ps")
class VoodooPs(VoodooForward):
    """List containers"""
    _cmd = "ps"


@Voodoo.subcommand("logs")
class VoodooLogs(VoodooForward):
    """View output from containers"""
    _cmd = "logs"


@Voodoo.subcommand("pull")
class VoodooPull(VoodooForward):
    """Pulls service images"""
    _cmd = "pull"


def main():
    Voodoo.run()
