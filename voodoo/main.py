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
from .hook import Deploy, GetMainService, InitRunDev, GenerateDevComposeFile
from datetime import datetime

compose = local['docker-compose']

__version__ = '2.6.7'


DEFAULT_CONF = {
    "verbose": True,
    "shared_eggs": True,
    "shared_gems": True,
    "odoo": "https://github.com/oca/ocb.git",
    "template": "https://github.com/akretion/voodoo-template.git",
    "maintainer_quality_tools":
        "https://github.com/OCA/maintainer-quality-tools",
    "env": "dev",
}

DOCKER_COMPOSE_PATH = 'docker-compose.yml'

import logging

client = docker.from_env()

logger = logging.getLogger('voodoo')
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


class Voodoo(cli.Application):
    PROGNAME = "voodoo"
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
        for key, value in DEFAULT_CONF.items():
            if key in config:
                new_config[key] = config[key]
            # Set Configuration
            setattr(self, key, new_config[key])

        # Update config file if needed
        if new_config != config:
            logger.info("The Voodoo Configuration have been updated, "
                        "please take a look to the new config file")
            if not os.path.exists(self.shared_folder):
                os.makedirs(self.shared_folder)
            config_file = open(config_path, 'w')
            config_file.write(yaml.dump(new_config, default_flow_style=False))
            logger.info("Update default config file at %s", config_path)
        if self.verbose:
            self.set_log_level()
            logger.debug(
                'You can change the default value in ~/.voodoo/config.yml')

    @cli.switch("--verbose", help="Verbose mode", group = "Meta-switches")
    def set_log_level(self):
        logger.setLevel(logging.DEBUG)
        logger.debug('Verbose mode activated')


class VoodooSub(cli.Application):

    def _exec(self, *args, **kwargs):
        self.parent._exec(*args, **kwargs)

    def _run(self, *args, **kwargs):
        self.parent._run(*args, **kwargs)

    def _get_main_service(self):
        for subcls in GetMainService.__subclasses__():
            service = subcls(self, logger).run()
            if service:
                logger.debug("Project detected : %s", service)
                return service
        raise_error("The project type failed to be defined")

    def run_hook(self, cls):
        def itersubclass(cls):
            list_cls = [cls]
            for subcls in cls.__subclasses__():
                list_cls += itersubclass(subcls)
            return list_cls
        for subcls in itersubclass(cls):
            if subcls._service == self.main_service:
                return subcls(self, logger).run()

    def _init_env(self, *args, **kwargs):
        self.env = self.parent.force_env or self.parent.env
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
        self.main_service = self._get_main_service()
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

VoodooSub.unbind_switches("--help-all", "-v", "--version")

@Voodoo.subcommand("deploy")
class VoodooDeploy(VoodooSub):
    """Deploy your application"""

    def _main(self):
        if self.env == 'dev':
            raise_error("Deploy can not be used in dev mode, "
                        "please configure .voodoo/config.yml")
        self.run_hook(Deploy)


@Voodoo.subcommand("run")
class VoodooRun(VoodooSub):
    """Start services and enter in your dev container

    After running the command you will be inside the container and
    you will have access to the ak cmd (see ak documenation)
    main command are 'ak run' and 'ak build'

    Note: the container is accessible with the following url :
    http://my_project.vd and http://my_plugin.my_project.vd
    """

    def _set_local_dev_network(self):
        existing_network = False
        for network in client.networks.list():
            if network.name == "vd":
                existing_network = True
        if not existing_network:
            ipam_pool = docker.types.IPAMPool(subnet="172.42.0.0/16")
            ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
            logger.info("Create '.vd' network")
            client.networks.create(
                'vd',
                driver="bridge",
                ipam=ipam_config)
        container = client.containers.list(
            all=True,
            filters={'name':'voodoo-proxy'})
        if container:
            container = container[0]
            if container.status != 'running':
                logger.info("Restart voodoo proxy")
                container.restart()
        else:
            logger.info("Start Voodoo proxy")
            client.containers.run(
                "akretion/voodoo-proxy",
                hostname="voodoo-proxy",
                name="voodoo-proxy",
                network_mode='vd',
                volumes=[
                    "/var/run/docker.sock:/tmp/docker.sock:ro",
                    "/etc/hosts:/app/hosts",
                    ],
                detach=True)

    def _main(self, *optionnal_command_line):
        if not optionnal_command_line:
            cmd = ['bash']
        else:
            cmd = list(optionnal_command_line)
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


@Voodoo.subcommand("open")
class VoodooOpen(VoodooSub):
    """Open a new session inside your dev container"""

    def _main(self, *args):
        project = get_project('.', [self.config_path])
        container = project.containers(
            service_names=[self.main_service], one_off=OneOffFilter.include)
        if container:
            self._exec('docker',
                       ["exec", "-ti", container[0].name, "bash"])
        else:
            raise_error("No container found for the service odoo "
                        "in the project %s" % project.name)


@Voodoo.subcommand("kill")
class VoodooKill(VoodooSub):
    """Kill all running container of the project"""

    def _main(self, *args):
        # docker compose do not kill the container odoo as is was run
        # manually, so we implement our own kill
        project = get_project('.', config_path=[
            self.config_path.decode('utf-8')])
        containers = project.containers(one_off=OneOffFilter.include)
        parallel_kill(containers, {'signal': 'SIGKILL'})


@Voodoo.subcommand("migrate")
class VoodooMigrate(VoodooSub):
    """Migrate your odoo project

    First you need to checkout the voodoo-upgrade template
    available here : https://github.com/akretion/voodoo-upgrade
    (It's a template a voodoo but based on open-upgrade'

    Then go inside the repository clonned and launch the migration

    * For migrating from 6.1 to 8.0 run:
        voodoo migrate -b 7.0,8.0
    * For migrating from 6.1 to 9.0 run:
        voodoo migrate -b 7.0,8.0,9.0
    * For migrating and loading a database run:
        voodoo migrate -b 7.0,8.0 --db-file=tomigrate.dump

    """

    db_file = cli.SwitchAttr(["db-file"])
    apply_branch = cli.SwitchAttr(
        ["b", "branch"],
        help="Branch to apply split by comma ex: 7.0,8.0",
        mandatory=True)
    _logs = []

    def log(self, message):
        print message
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
            self._log("Migrate to version %s in %s" % (version, end-start))
        for log in self._logs:
            logger.info(log)


@Voodoo.subcommand("new")
class VoodooNew(VoodooSub):
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


class VoodooForward(VoodooSub):
    _cmd = None

    def _main(self, *args):
        return self._run(self.compose[self._cmd.split(' ')])


@Voodoo.subcommand("build")
class VoodooBuild(VoodooForward):
    """Build or rebuild services"""
    _cmd = "build"


@Voodoo.subcommand("up")
class VoodooUp(VoodooForward):
    """Start all services in detached mode"""
    _cmd = "up -d"


@Voodoo.subcommand("down")
class VoodooDown(VoodooForward):
    """Stop all services"""
    _cmd = "down"


@Voodoo.subcommand("ps")
class VoodooPs(VoodooForward):
    """List containers"""
    _cmd = "ps"


@Voodoo.subcommand("logs")
class VoodooLogs(VoodooForward):
    """View output from containers"""
    _cmd = "logs -f --tail=100"


@Voodoo.subcommand("pull")
class VoodooPull(VoodooForward):
    """Pulls service images"""
    _cmd = "pull"


def main():
    Voodoo.run()
