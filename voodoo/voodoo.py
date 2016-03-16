#!/usr/bin/env python
# coding: utf-8

import socket
import logging
from subprocess import check_call
from subprocess import check_output
from subprocess import CalledProcessError
import os
import shutil
import yaml
import six
import sys
import voodoo

from compose import config
from compose.cli.main import TopLevelCommand
from compose.cli.errors import UserError

log = logging.getLogger(__name__)

TEMPLATE = "https://github.com/akretion/voodoo-template.git"
ODOO_GIT = "https://github.com/OCA/OCB.git"

DEFAULT_CONF = {
    "shared_eggs": True,
    "shared_odoo": False,
    "gitconfig": "~/.gitconfig",
    "used_odoo_repo": "oca",
    "odoo_repo_list": {
        "oca": "https://github.com/oca/ocb.git",
    },
}
OCA_HELPER_REPOSITORIES = [
    'maintainer-tools',
    'maintainer-quality-tools',
    'pylint-odoo',
]


# inspired from http://stackoverflow.com
# /questions/8100166/inheriting-methods-docstrings-in-python
def fix_docs(cls):
    for name, func in vars(cls).items():
        if not func.__doc__:
            for parent in cls.__bases__:
                if hasattr(parent, name):
                    parfunc = getattr(parent, name)
                    if parfunc and getattr(parfunc, '__doc__', None):
                        func.__doc__ = parfunc.__doc__.replace(
                            'docker-compose', 'voodoo')
                        break
    return cls


def voodoo_load_yaml(file_name):
    try:
        # Load default voodoo config
        default_config_path = os.path.join(
            os.path.expanduser("~"), '.voodoo', 'config.yml')
        with open(default_config_path, 'r') as fh:
            voodoo_config = yaml.safe_load(fh)

        with open(file_name, 'r') as fh:
            #Load custom config
            config = yaml.safe_load(fh)

            #update voodoo config
            voodoo_config.update(config.pop('voodoo', {}))

            # share .voodoo folder in voodoo
            home = os.path.expanduser("~")
            shared = os.path.join(home, '.voodoo', 'shared')
            config['odoo']['volumes'].append('%s:%s' % (shared, shared))

            # Add gitconfig in voodoo
            if 'gitconfig' in voodoo_config:
                gitconfig = os.path.expanduser(voodoo_config['gitconfig'])
                config['odoo']['volumes'].append(
                    '%s:/home/devstep/.gitconfig' % (gitconfig))

            #Add environment variable
            config['odoo']['environment'] += [
                'SHARED_FOLDER=%s' % shared,
                'SHARED_EGGS=%s' % str(voodoo_config['shared_eggs']).lower(),
                ]
            return config
    except IOError as e:
            raise UserError(six.text_type(e))

config.load_yaml = voodoo_load_yaml


@fix_docs
class VoodooCommand(TopLevelCommand):
    """Fast, isolated development environments using Docker.

    Usage:
      voodoo [options] [COMMAND] [ARGS...]
      voodoo -h|--help

    Options:
      --verbose                 Show more output
      --version                 Print version and exit
      -f, --file FILE           Specify an alternate compose file
                                (default: voodoo.yml)
      -p, --project-name NAME   Specify an alternate project name
                                (default: directory name)

    Commands:
      build     Build or rebuild services
      help      Get help on a command
      kill      Kill containers
      logs      View output from containers
      new       Create a new project
      open      Open a new session inside the docker
      port      Print the public port for a port binding
      ps        List containers
      pull      Pulls service images
      rm        Remove stopped containers
      run       Run a one-off command
      scale     Set number of containers for a service
      start     Start services
      stop      Stop services
      restart   Restart services
      up        Create and start containers
      chefdk    Chef Development Kit wrapper

    """

    def load_project_config(self, options):
        explicit_config_path = options.get('--file')\
            or os.environ.get('COMPOSE_FILE')\
            or os.environ.get('FIG_FILE')
        config_path = self.get_config_path(file_path=explicit_config_path)
        try:
            with open(config_path, 'r') as fh:
                config = yaml.safe_load(fh)
                voodoo_config = config.pop('voodoo', {})
                self.set_config(voodoo_config)
        except IOError as e:
            raise UserError(six.text_type(e))

    def set_config(self, config):
        for key in DEFAULT_CONF:
            if key in config:
                setattr(self, key, config[key])

    def _generate_default_home_config(self, config_path):
        # Create folders
        if not os.path.exists(self.shared_folder):
            os.makedirs(self.shared_folder)
        erp_folder = os.path.join(self.home, '.voodoo', 'erp_helper')
        if not os.path.exists(erp_folder):
            os.makedirs(erp_folder)
            # Clone Quality repos
            log.info("Start cloning ERP helpers tools")
            for repo in OCA_HELPER_REPOSITORIES:
                check_call([
                    "git", "clone",
                    "https://github.com/OCA/%s.git" % repo, erp_folder])
        # Set configuration
        config_file = open(config_path, 'w')
        config_file.write(yaml.dump(DEFAULT_CONF, default_flow_style=False))
        log.info("Create default config file at %s" % config_path)

    def __init__(self, *args, **kwargs):
        super(VoodooCommand, self).__init__(*args, **kwargs)
        self.home = os.path.expanduser("~")
        self.shared_folder = os.path.join(self.home, '.voodoo', 'shared')
        self.compose_config = None

        config_path = os.path.join(self.home, '.voodoo', 'config.yml')

        # Create default config file in home if missing
        if not os.path.isfile(config_path):
            self._generate_default_home_config(config_path)

        # Load Configuration
        config_file = open(config_path, 'r')
        config = DEFAULT_CONF.copy()
        config.update(yaml.safe_load(config_file))
        self.set_config(config)

    def clone_odoo(self, ref_path, dest_path):
        # TODO to improve the speed of initial config
        # We may implement latter a caching system
        # The idea will to have an existing copy of the repo
        # and just mv it here
        # and an new copy of repo while be the generated in background
        log.info("Start cloning odoo from local odoo")
        check_call(["git", "clone", "file://%s" % ref_path, dest_path])

    def get_odoo(self, odoo_path):
        odoo_cache_path = os.path.join(self.shared_folder, 'cached_odoo')
        if not os.path.exists(odoo_cache_path):
            os.makedirs(odoo_cache_path)
        odoo_ref_path = os.path.join(odoo_cache_path, self.used_odoo_repo)
        if not os.path.exists(odoo_ref_path):
            log.info(
                "First run of Voodoo; there is no Odoo repo in %s! "
                "Will now download Odoo from Github, "
                "this can take a while...\n"
                "If you already have a local Odoo repo (from OCA) "
                "then you can you can abort the download "
                "and paste your repo or make a symbolink link in %s",
                odoo_ref_path, odoo_ref_path)
            if self.odoo_repo_list.get(self.used_odoo_repo, False):
                git_repo = self.odoo_repo_list[self.used_odoo_repo]
            else:
                log.error(
                    "Error: The repo '%s' is not in the repo list.",
                    self.used_odoo_repo)
                log.error("Please add it in the voodoo config file.")
                sys.exit(1)
            check_call(["git", "clone", git_repo, odoo_ref_path])
        if self.shared_odoo:
            shared_odoo_path = os.path.join(
                self.shared_folder,
                'shared_odoo',
                self.shared_odoo,
                )
            if not os.path.exists(shared_odoo_path):
                log.info(
                    "Shared odoo is activated, but there is no shared "
                    "repository in %s",  shared_odoo_path)
                self.clone_odoo(odoo_ref_path, shared_odoo_path)
            log.info("Create symlink from %s to %s",
                     shared_odoo_path, odoo_path)
            check_call(['ln', '-s', shared_odoo_path, odoo_path])
        else:
            self.clone_odoo(odoo_ref_path, odoo_path)

    def chefdk(self, project, options):
        if not os.path.isfile('.kitchen.yml'):
            log.warning(".kitchen.yml file is missing.\n"
                     "-> Creating default .kitchen.yml\n"
                     "You should now edit it and at least\n"
                     "set the server ip and run the command again")
            kitchen_path = os.path.join(os.path.dirname(voodoo.__file__),
                                        'config/.kitchen.yml')
            shutil.copy2(kitchen_path, '.kitchen.yml')
            return False
        ip_part = check_output(["grep", "^  hostname:", ".kitchen.yml"])
        ip = ip_part.replace("hostname:", "").strip()
        if ip != "SERVER_IP":
            pwd = os.getcwd()
            bundler_cmd = sys.argv[2:] or ["kitchen", "converge"]
            home = os.path.expanduser("~")
            cmd = ['docker', 'run', '-ti',
                   '-v', "%s/.ssh:/root/.ssh_host" % (home,),
                   '-v', "%s:/workspace" % (pwd,),
                   'akretion/chefdk'] + bundler_cmd
            res = check_call(cmd)

            try:
                if check_output(["grep", 'remote "clodoo"', ".git/config"]):
                    check_call(["git", "remote", "remove", "clodoo"])
            except CalledProcessError:
                pass
            try:
                app = list(reversed(os.getcwd().split('/')))[0]
                check_call(["git", "remote", "add",
                            "clodoo", "akretion@%s:%s" % (ip, app)])
                log.info("clodoo remote set to akretion@%s:%s" % (ip, app))
            except CalledProcessError:
                pass
            return res
        else:
            log.warning("you should configure your own SERVER_IP"
                        "in .kitchen.yml and run the command again")

    def run(self, project, options):
        if not options.get('SERVICE'):
            options['SERVICE'] = 'odoo'
        if not options.get('--service-ports'):
            options['--service-ports'] = True
        if not options.get('COMMAND'):
            options['COMMAND'] = 'bash'
        if not os.path.exists('parts'):
            os.makedirs('parts')
        odoo_path = os.path.join('parts', 'odoo')
        if not os.path.exists(odoo_path):
            self.get_odoo(odoo_path)
        return super(VoodooCommand, self).run(project, options)

    def get_config_path(self, file_path=None):
        if not file_path:
            file_path = 'voodoo.yml'
        return super(VoodooCommand, self).get_config_path(file_path=file_path)

    def new(self, project, options):
        """
        Start a new project
        Usage: new [options] PROJECT
        """
        check_call(["git", "clone", TEMPLATE, options['PROJECT']])
# TODO the following may work if we deal with CWD
#        check_call(["git", "remote", "remove", "origin"])

    def open(self, project, options):
        """
        Open an new terminal in voodoo
        Usage: open
        """
        container = project.containers(service_names=['odoo'], one_off=True)
        if container:
            check_call(["docker", "exec", "-ti", container[0].name, "bash"])
        else:
            log.error("No container found for the service odoo "
                      "in the project %s" % project.name)

    def service(self, project, options):
        """
        Link containers
        Usage: service [options] COMMAND SERVICE_NAME
        """
        container = project.containers(service_names=['odoo'], one_off=True)
        if container:
            log.error("Please stop the container before linking a new container.")
            sys.exit(1)
        if options['COMMAND'] == 'add':
            config_path = self.get_config_path()
            old_config_file = open(config_path, 'r')
            old_config = old_config_file.read()
            old_config_file.close()
            new_config = yaml.safe_load(old_config)
            if (new_config['odoo'].get('links') and
                options['SERVICE_NAME'] in new_config['odoo']['links']):
                log.error(
                    "The service '%s' has already been added to this project."
                    % options['SERVICE_NAME'])
                sys.exit(1)
            elif new_config['odoo'].get('links'):
                new_config['odoo']['links'].append(options['SERVICE_NAME'])
            else:
                new_config['odoo']['links'] = [options['SERVICE_NAME']]
            service_path = os.path.join(os.path.dirname(voodoo.__file__),
                                        'config/service.yml')
            service_file = open(service_path, 'r')
            service_config = yaml.safe_load(service_file)
            if not options['SERVICE_NAME'] in service_config:
                log.error(
                    "The service '%s' is not defined in the 'service.yml' file."
                    % options['SERVICE_NAME'])
                sys.exit(1)
            new_config.update({
                options['SERVICE_NAME']: service_config[options['SERVICE_NAME']]
            })
            config_file = open(config_path, 'w')
            config_file.write(yaml.dump(new_config, default_flow_style=False))
            config_file.close()
        else:
            log.error("The command '%s' has not been implemented yet"
                      % options['COMMAND'])
            sys.exit(1)
        return self.dispatch(['run'], {})


    def perform_command(self, options, handler, command_options):
        # no need of project params for new method
        if options['COMMAND'] == 'new':
            # Skip looking up the compose file.
            handler(None, command_options)
            return
        self.load_project_config(options)
        return super(VoodooCommand, self).perform_command(
            options, handler, command_options)

    def dispatch(self, *args, **kwargs):
        if args and args[0] and args[0][0] == 'chefdk':
            return self.chefdk(VoodooCommand, self)
        # Inject default value for run method
        if args and args[0] and args[0][0] == 'run' and len(args[0]) == 1:
            args[0].append('odoo')
        return super(VoodooCommand, self).dispatch(
            *args, **kwargs)
