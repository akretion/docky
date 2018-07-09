#!/usr/bin/env python
# coding: utf-8

from plumbum import cli, local
from plumbum.cmd import git, docker, grep, sed
from plumbum.commands.modifiers import FG, TF, BG
from plumbum.cli.terminal import choose, ask
import os
import sys
from compose.cli.command import get_project
from compose.project import OneOffFilter
from compose.parallel import parallel_kill
import yaml
import docker
from .hook import InitRunDev, GenerateDevComposeFile
from datetime import datetime

compose = local['docker-compose']

__version__ = '3.0.6'


DEFAULT_CONF = {
    "verbose": True,
    "shared_eggs": True,
    "shared_gems": True,
    "odoo": "https://github.com/oca/ocb.git",
    "template": "https://github.com/akretion/docky-template.git",
    "maintainer_quality_tools":
        "https://github.com/OCA/maintainer-quality-tools",
    "env": "dev",
}

DOCKER_COMPOSE_PATH = 'docker-compose.yml'
DOCKY_PATH = 'docky.yml'

DOCKY_NETWORK_NAME = 'vd'
DOCKY_NETWORK_SUBNET = '172.42.0.0/16'
DOCKY_NETWORK_GATEWAY = '172.42.0.1'
DOCKY_NETWORK_OPTIONS = {
    'com.docker.network.bridge.name': DOCKY_NETWORK_NAME,
    'com.docker.network.bridge.host_binding_ipv4': '127.0.0.1',
}

DOCKY_PROXY_IMAGE = "quay.io/akretion/docky-proxy:20180507"
DOCKY_PROXY_NAME = "docky-proxy"

import logging

client = docker.from_env()

logger = logging.getLogger('docky')
formatter = logging.Formatter("%(message)s")
logger.setLevel(logging.INFO)

# Optionnal code for colorized log
from rainbow_logging_handler import RainbowLoggingHandler
handler = RainbowLoggingHandler(
    sys.stderr,
    color_message_info = ('green' , None , True),
)
handler.setFormatter(formatter)
logger.addHandler(handler)
# End of optional code


def raise_error(message):
    logger.error(message)
    sys.exit(0)


def get_containers(config_path, service=None):
    project = get_project('.', [config_path])
    kwargs = {'one_off': OneOffFilter.include}
    if service:
        kwargs['service_names'] = [service]
    return project.containers(**kwargs)


class Docky(cli.Application):
    PROGNAME = "docky"
    VERSION = __version__
    SUBCOMMAND_HELPMSG = None

    dryrun = cli.Flag(
        ["dry-run"],
        help="Dry run mode",
        group = "Meta-switches")
    force_env = cli.SwitchAttr(
        ["e", "env"],
        help="Environment flag",
        group = "Switches")

    def _run(self, cmd, retcode=FG):
        """Run a command in a new process and log it"""
        logger.debug(str(cmd).replace('/usr/local/bin/', ''))
        if (self.dryrun):
            logger.info(cmd)
            return True
        return cmd & retcode

    def _exec(self, cmd, args=[]):
        """Run a command in the same process and log it
        this will replace the current process by the cmd"""
        logger.debug(cmd + ' '.join(args))
        if (self.dryrun):
            logger.info("os.execvpe (%s, %s, env)", cmd, [cmd] + args)
            return True
        os.execvpe(cmd, [cmd] + args, local.env)

    def _get_home(self):
        return os.path.expanduser("~")

    def __init__(self, executable):
        super(Docky, self).__init__(executable)
        self.home = self._get_home()
        self.shared_folder = os.path.join(self.home, '.docky', 'shared')
        config_path = os.path.join(self.home, '.docky', 'config.yml')

        # Read existing configuration
        if os.path.isfile(config_path):
            config_file = open(config_path, 'r')
            config = yaml.safe_load(config_file)
        else:
            config = {}

        # Update configuration with default value and remove dead key
        new_config = DEFAULT_CONF.copy()
        for key, value in DEFAULT_CONF.items():
            if key in config:
                new_config[key] = config[key]
            # Set Configuration
            setattr(self, key, new_config[key])

        # Update config file if needed
        if new_config != config:
            logger.info("The Docky Configuration have been updated, "
                        "please take a look to the new config file")
            if not os.path.exists(self.shared_folder):
                os.makedirs(self.shared_folder)
            config_file = open(config_path, 'w')
            config_file.write(yaml.dump(new_config, default_flow_style=False))
            logger.info("Update default config file at %s", config_path)
        if self.verbose:
            self.set_log_level()
            logger.debug(
                'You can change the default value in ~/.docky/config.yml')

        # Reading local configuration
        if os.path.isfile(DOCKY_PATH):
            self.config = yaml.safe_load(open(DOCKY_PATH, 'r'))
        else:
            raise_error(
                '%s file is missing. Minimal file is a yaml file with:\n'
                ' service: your_service\nex:\n service: odoo' % DOCKY_PATH)


    @cli.switch("--verbose", help="Verbose mode", group = "Meta-switches")
    def set_log_level(self):
        logger.setLevel(logging.DEBUG)
        logger.debug('Verbose mode activated')


class DockySub(cli.Application):

    def _exec(self, *args, **kwargs):
        self.parent._exec(*args, **kwargs)

    def _run(self, *args, **kwargs):
        self.parent._run(*args, **kwargs)

    def run_hook(self, cls):
        def getsubclass(cls, service):
            for subcls in cls.__subclasses__():
                print("subcls", subcls._service)
                if subcls._service == service:
                    return subcls
                else:
                    service_cls = getsubclass(subcls, service)
                    if service_cls:
                        return service_cls
            return None
        service_cls = getsubclass(cls, self.main_service)
        if not service_cls:
            service_cls = cls
        return service_cls(self, logger).run()

    def _init_env(self, *args, **kwargs):
        self.env = self.parent.force_env or self.parent.env
        self.config = self.parent.config
        config_path = '.'.join([self.env, DOCKER_COMPOSE_PATH])
        if self.env == 'dev':
            self.config_path = config_path
        elif local.path(config_path).is_file():
            self.config_path = config_path
        elif local.path(DOCKER_COMPOSE_PATH).is_file():
            self.config_path = DOCKER_COMPOSE_PATH
        else:
            raise_error(
                "There is not %s.%s or %s file, please add one"
                % (self.env, DOCKER_COMPOSE_PATH, DOCKER_COMPOSE_PATH))
        self.main_service = self.parent.config['service']
        if self.env == 'dev':
            if not local.path(self.config_path).isfile():
                generate = ask(
                    "There is not dev.docker-compose.yml file.\n"
                    "Do you want to generate one automatically",
                    default=True)
                if generate:
                    self.run_hook(GenerateDevComposeFile)
                else:
                    raise_error("No dev.docker-compose.yml file, abort!")
        self.compose = compose['-f', self.config_path]

    def main(self, *args, **kwargs):
        self._init_env()
        self._main(*args, **kwargs)

DockySub.unbind_switches("--help-all", "-v", "--version")


@Docky.subcommand("deploy")
class DockyDeploy(DockySub):
    """Deploy your application"""

    def _main(self):
        raise_error("Not implemented")

class DockyExec(object):

    root = cli.Flag(
        ["root"],
        help="Run or open as root",
        group = "Meta-switches")

    def _use_specific_user(self):
        return not self.root and self.config.get('user')


@Docky.subcommand("run")
class DockyRun(DockySub, DockyExec):
    """Start services and enter in your dev container

    After running the command you will be inside the container and
    you will have access to the ak cmd (see ak documenation)
    main command are 'ak run' and 'ak build'

    Note: the container is accessible with the following url :
    http://my_project.vd and http://my_plugin.my_project.vd
    """


    def _set_local_dev_network(self):

        net = DOCKY_NETWORK_NAME

        if not client.networks.list(net):
            ipam_pool = docker.types.IPAMPool(
                subnet=DOCKY_NETWORK_SUBNET,
                iprange=DOCKY_NETWORK_SUBNET,
                gateway=DOCKY_NETWORK_GATEWAY,
            )
            ipam_config = docker.types.IPAMConfig(
                pool_configs=[ipam_pool])

            logger.info("Create '.%s' network" % net)

            client.networks.create(
                net,
                driver="bridge",
                ipam=ipam_config,
                options=DOCKY_NETWORK_OPTIONS,
            )

        container = client.containers.list(
            all=True,
            filters={'name': DOCKY_PROXY_NAME})

        if container:
            container = container[0]
            if container.status != 'running':
                logger.info("Restart docky proxy")
                container.restart()
        else:
            logger.info("Start Docky proxy")
            client.containers.run(
                DOCKY_PROXY_IMAGE,
                hostname=DOCKY_PROXY_NAME,
                name=DOCKY_PROXY_NAME,
                network_mode=net,
                volumes=[
                    "/var/run/docker.sock:/tmp/docker.sock:ro",
                    "/etc/hosts:/app/hosts",
                    ],
                detach=True)

    def _check_running(self):
        if get_containers(self.config_path, self.main_service):
            raise_error("This container is already running, kill it or "
                        "use open to go inside")

    def _main(self, *optionnal_command_line):
        self._check_running()
        if self._use_specific_user():
            cmd = ['gosu', self.config['user']]
        else:
            cmd = []
        if not optionnal_command_line:
            cmd.append('bash')
        else:
            cmd += list(optionnal_command_line)
        if self.env == 'dev':
            self._set_local_dev_network()
            self.run_hook(InitRunDev)
        # Remove useless dead container before running a new one
        self._run(self.compose['rm', '-f'])
        config = yaml.safe_load(open(self.config_path, 'r'))
        for name, service in config['services'].items():
            for env in service.get('environment', []):
                if 'VIRTUAL_HOST=' in env:
                    dns = env.replace('VIRTUAL_HOST=', '')
                    logger.info(
                        "The service %s is accessible on http://%s"
                        % (name, dns))
        self._exec('docker-compose', [
            '-f', self.config_path,
            'run', '--rm', '--service-ports',
            self.main_service] + cmd)


@Docky.subcommand("open")
class DockyOpen(DockySub, DockyExec):
    """Open a new session inside your dev container"""

    def _main(self, *args):
        container = get_containers(self.config_path, self.main_service)
        if container:
            cmd = ["exec", "-ti", container[0].name]
            if self._use_specific_user():
                cmd += ['gosu', self.config['user'], 'bash']
            else:
                cmd.append('bash')
            self._exec('docker', cmd)
        else:
            raise_error(
                "No container found for the service %s" % self.main_service)


@Docky.subcommand("kill")
class DockyKill(DockySub):
    """Kill all running container of the project"""

    def _main(self, *args):
        # docker compose do not kill the container odoo as is was run
        # manually, so we implement our own kill
        containers = get_containers(self.config_path)
        parallel_kill(containers, {'signal': 'SIGKILL'})


@Docky.subcommand("migrate")
class DockyMigrate(DockySub):
    """Migrate your odoo project

    First you need to checkout the docky-upgrade template
    available here : https://github.com/akretion/docky-upgrade
    (It's a template a docky but based on open-upgrade'

    Then go inside the repository clonned and launch the migration

    * For migrating from 6.1 to 8.0 run:
        docky migrate -b 7.0,8.0
    * For migrating from 6.1 to 9.0 run:
        docky migrate -b 7.0,8.0,9.0
    * For migrating and loading a database run:
        docky migrate -b 7.0,8.0 --db-file=tomigrate.dump

    """

    db_file = cli.SwitchAttr(["db-file"])
    apply_branch = cli.SwitchAttr(
        ["b", "branch"],
        help="Branch to apply split by comma ex: 7.0,8.0",
        mandatory=True)
    _logs = []

    def log(self, message):
        print(message)
        self._logs.append(message)

    def _run_ak(self, *params):
        start = datetime.now()
        cmd = "ak " + " ".join(params)
        self.log("Launch %s" % cmd)
        self.compose("run", "odoo", "ak", *params)
        end = datetime.now()
        self.log("Run %s in %s" % (cmd, end-start))

    def _main(self):
        if self.main_service != 'odoo':
            raise_error("This command is used only for migrating odoo project")
        versions = self.apply_branch.split(',')
        logs = ["\n\nMigration Log Summary:\n"]
        first = True
        for version in versions:
            start = datetime.now()
            self._run(git["checkout", version])
            self._run_ak("build")
            if self.db_file and first:
                self._run_ak("db", "load", "--force", self.db_file)
                first = False
            self._run_ak("upgrade")
            self._run_ak("db", "dump", "--force", "migrated_%s.dump" % version)
            end = datetime.now()
            self.log("Migrate to version %s in %s" % (version, end-start))
        for log in self._logs:
            logger.info(log)


@Docky.subcommand("new")
class DockyNew(DockySub):
    """Create a new project"""

    def main(self, name):
        versions = ['11.0', '10.0', '9.0', '8.0', '7.0', 'master']
        version = choose(
            "Select your Odoo project template",
            versions,
            default = "10.0")
        self._run(git["clone", self.parent.template, name])
        with local.cwd(name):
            self._run(git["checkout", version])


class DockyForward(DockySub):
    _cmd = None

    def _main(self, *args):
        return self._run(self.compose[self._cmd.split(' ')])


@Docky.subcommand("build")
class DockyBuild(DockyForward):
    """Build or rebuild services"""
    _cmd = "build"


@Docky.subcommand("up")
class DockyUp(DockyForward):
    """Start all services in detached mode"""
    _cmd = "up -d"


@Docky.subcommand("down")
class DockyDown(DockyForward):
    """Stop all services"""
    _cmd = "down"


@Docky.subcommand("ps")
class DockyPs(DockyForward):
    """List containers"""
    _cmd = "ps"


@Docky.subcommand("logs")
class DockyLogs(DockyForward):
    """View output from containers"""
    _cmd = "logs -f --tail=100"


@Docky.subcommand("pull")
class DockyPull(DockyForward):
    """Pulls service images"""
    _cmd = "pull"


def main():
    Docky.run()
