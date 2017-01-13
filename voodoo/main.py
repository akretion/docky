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
from .hook import Deploy, GetMainService, InitRunDev, GenerateDevComposeFile
compose = local['docker-compose']

__version__ = '2.3.0'


DEFAULT_CONF = {
    "shared_eggs": True,
    "shared_gems": True,
    "odoo": "https://github.com/oca/ocb.git",
    "template": "https://github.com/akretion/voodoo-template.git",
    "env": "dev",
}

DOCKER_COMPOSE_PATH = 'docker-compose.yml'

import logging


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

    dryrun = cli.Flag(["dry-run"], help="Dry run mode")
    force_env = cli.SwitchAttr(["e", "env"], help="Environment flag")

    def _run(self, cmd, retcode=FG):
        """Run a command in a new process and log it"""
        logger.debug(cmd)
        if (self.dryrun):
            logger.info(cmd)
            return True
        return cmd & retcode

    def _exec(self, cmd, args=[]):
        """Run a command in the same process and log it
        this will replace the current process by the cmd"""
        logger.debug([cmd, args])
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

    @cli.switch("--verbose", help="Verbose mode")
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

    def __init__(self, *args, **kwargs):
        super(VoodooSub, self).__init__(*args, **kwargs)
        if args and args[0] == 'voodoo new':
            return
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


@Voodoo.subcommand("deploy")
class VoodooDeploy(VoodooSub):
    """Deploy your application"""

    def main(self):
        if self.env == 'dev':
            raise_error("Deploy can not be used in dev mode, "
                        "please configure .voodoo/config.yml")
        self.run_hook(Deploy)


@Voodoo.subcommand("run")
class VoodooRun(VoodooSub):
    """Start services and enter in your dev container"""

    def main(self, *optionnal_command_line):
        if not optionnal_command_line:
            cmd = ['bash']
        else:
            cmd = list(optionnal_command_line)
        if self.env == 'dev':
            self.run_hook(InitRunDev)
        # Remove useless dead container before running a new one
        self._run(self.compose['rm', '-f'])
        self._exec('docker-compose', [
            '-f', self.config_path,
            'run', '--service-ports',
            self.main_service] + cmd)


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
            raise_error("No container found for the service odoo "
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
        versions = ['10.0', '9.0', '8.0', '7.0']
        version = choose(
            "Select your Odoo project template",
            versions,
            default = "10.0")
        self._run(git["clone", self.parent.template, name])
        with local.cwd(name):
            self._run(git["checkout", version])


class VoodooForward(VoodooSub):
    _cmd = None

    def main(self, *args):
        return self._run(self.compose[self._cmd.split(' ')])


@Voodoo.subcommand("build")
class VoodooBuild(VoodooForward):
    """Build or rebuild services"""
    _cmd = "build"


@Voodoo.subcommand("up")
class VoodooUp(VoodooForward):
    """Start all services"""
    _cmd = "up"


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
    _cmd = "logs -f"


@Voodoo.subcommand("pull")
class VoodooPull(VoodooForward):
    """Pulls service images"""
    _cmd = "pull"


def main():
    Voodoo.run()
