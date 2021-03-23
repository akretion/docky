Introduction
=================

docky is a multi-purpose tool that adds some functionality for creating, running and managing docker-compose.yml files.


History & motivation
--------------------

This project was initially created for building Odoo environments without effort based on docker-compose and docker.

Step by step, we have made it generic and now also use it for our rails and ruby development.


How it works
---------------

Docky integrates a default docker-compose file generator and simplifies running of docker containers.

Once your setup is done, docky depends on docker-compose and uses the same file. Except for some convenience features, you will mostly get the same results if you run the generated docker-compose.yml file through docker-compose or docky.


Requirements
------------

docker-ce : https://docs.docker.com/install/ (or podman)


Installation
------------

Docky is available from pypi

.. code-block:: shell

    pip install docky
    # or with pipx : pipx install docky --include-deps


Update Docky
-------------

.. code-block:: shell

    pip install docky --upgrade
    # or with pipx : pipx upgrade docky --include-deps


Usage: commands
---------------

.. code-block:: shell

    docky init

Bootstraps a odoo project using a template (https://github.com/akretion/docky-odoo-template)
This will ask you a series of questions to create customized `.env <https://docs.docker.com/compose/env-file/>`_ and docker-compose.yml files that you can further edit.
Note that the template presumes that you have a running Traefik container on the "traefik" docker network.

For more information on other commands, use docky --help and check the `documentation <https://github.com/akretion/docky/blob/master/doc/command_line.rst>`_.


Usage: labels
-------------

The label docky.main.service and docky.user

.. code-block:: shell

    docky.main.service: odoo
    docky.user: odoo

Allows you to define the main service of your docker-compose.yml file, and to specify the command line user for the container when you run for example 'docky run'.


Usage: recommendations
----------------------

* Use `ak <https://github.com/akretion/ak>`_ to build your project.
* When developing, if you are on several projects at once, it quickly becomes a mess to manage different ports of your containers. We recommend usage of Traefik. Here is an example docker-compose.yml file for local development purposes:

.. code-block:: yaml

    version: "3.7"
    services:
        traefik:
        image: "traefik:v2.1"
        restart: always
        container_name: "traefik"
        command:
            - "--api.insecure=true"
            - "--providers.docker=true"
            - "--providers.docker.exposedbydefault=false"
            - "--entrypoints.web.address=:80"
        ports:
            - "127.0.0.1:80:80"
            - "127.0.0.1:8080:8080"
        volumes:
            - "/var/run/docker.sock:/var/run/docker.sock:ro"
        networks:
        - traefik

    networks:
        traefik:
            name: traefik

More info about Traefik config on this repo: https://github.com/akretion/traefik-template


Troubleshooting
---------------

To avoid issues with line wrapping with "docky open" please use a version of docker > to  18.06.0-ce
see : https://github.com/docker/compose/issues/6151


Changelog
----------

version 7.0.5
- fix requirements.txt

version 7.0.4
- use `copier` for managing the template
- drop python 3.5 support

version 7.0.0

- remove the need of docky config file in $HOME
- use .env to be more compatible with docker-compose
- improve templates
- create init command
- heavy refactoring


version 6.0.0

- refactor remove proxy code and use traefik
- remove docky.yml now you must use labels on services (see doc)
- add option "--service=myservice" on docky run and docky open

version 5.0.0:

- Resolve mac compatibility by remove proxy code that use a mounted version of etc/hosts
  now you need to install dnsmasq.
  This should also solve windows compatibilty by using the local dns https://stackoverflow.com/questions/138162/wildcards-in-a-windows-hosts-file?answertab=votes#tab-top
- Solve issue with project name in multi user env (the name is based on user + directory name)
- Add possibility to specify the service for run, open, logs, kill, down, restart, start cmd
  for example now you can do "docky open db" to open a terminal on the db server
  or you can restart a service like "docky restart varnish"
- Solve issue with missing aliases name
- Solve issue with missing environment variable with docky open (now we use a monkey-pacthed version of docker-compose exec)
- Fix documentation build
- Improve docky none specific cmd to a project to be run without project.
  For example, you can use docky help, docky proxy outside of a directory project
