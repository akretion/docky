Introduction
=================

docky : Make docker and docker-compose simply !


History
----------
This project was initialy created for building odoo environments without effort based on docker-compose and docker

Step by step we make it generic and now we also use it for our rails, ruby developpment

How it works
---------------

Docky is depend on docker-compose and use exactly the same file (so you can move from docker-compose to docky and vice-versa without any effort)

Docky just make docker-compose simplier and integrate a default docker-compose file generator

Requirements
------------

You need to install docker-ce : https://docs.docker.com/install/ (or podman)


Installation Docky 
------------------

Docky is available from pypi

.. code-block:: shell

    pip install docky
    # or with pipx : pipx install docky --include-deps


Update Docky
-------------

.. code-block:: shell

    pip install docky --upgrade
    # or with pipx : pipx upgrade docky --include-deps

Configuration:
--------------

Bootstrap a project with:

.. code-block:: shell

    docky init

It will create you a .env file you have to edit.
You can also start from a template like this one : https://github.com/akretion/docky-odoo-template

Build a project
---------------

Very recommended: use `ak` to build the projet. Follow the documentation here : https://github.com/akretion/ak



Docky Labels
~~~~~~~~~~~~~

The label docky.main.service and docky.user

.. code-block:: shell

    docky.main.service: odoo
    docky.user: odoo

Allow to define the main service of your docker compose and the user that should be user to enter in the container

Getting Started
---------------------

Use docky --help

But basically `docky run is` your friend

READ the documentation: `Docky documentation <https://github.com/akretion/docky/blob/master/doc/command_line.rst>`_


[Optionnal] Automatic Proxy - Multiproject setup
------------------------------------------------

When doing dev, is quickly a mess to manage the port of your containers.
We recommand to use traefik. You can find more information.


Troubleshooting
--------------------

To avoid issue with line wrapping with "docky open" please use a version of docker > to  18.06.0-ce
see : https://github.com/docker/compose/issues/6151


Changelog
----------

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
