#!/usr/bin/env python
# coding: utf-8

from inspect import getdoc
import logging
import sys

from compose.cli.main import setup_logging, parse_doc_section
from compose.project import NoSuchService, ConfigurationError
from compose.cli.docopt_command import NoSuchCommand
from compose.cli.errors import UserError
from docker.errors import APIError
from compose.service import BuildError
from .voodoo import VoodooCommand

log = logging.getLogger(__name__)


def main():
    setup_logging()
    try:
        command = VoodooCommand()
        command.sys_dispatch()
    except KeyboardInterrupt:
        log.error("\nAborting.")
        sys.exit(1)
    except (UserError, NoSuchService, ConfigurationError) as e:
        log.error(e.msg)
        sys.exit(1)
    except NoSuchCommand as e:
        log.error("No such command: %s", e.command)
        log.error("")
        log.error("\n".join(
            parse_doc_section("commands:", getdoc(e.supercommand))))
        sys.exit(1)
    except APIError as e:
        log.error(e.explanation)
        sys.exit(1)
    except BuildError as e:
        log.error("Service '%s' failed to build: %s"
                  % (e.service.name, e.reason))
        sys.exit(1)

main()
