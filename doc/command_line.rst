Command line documentation
============================

Usage:
    docky [OPTIONS] [SOUS_COMMANDE [OPTIONS]] args...

Meta-options:
    -h, --help         Print help messages and quits
    --help-all         Prints help messages of all sub-commands and quits
    -v, --version      Print version of cli
    --verbose          Verbose mode

Sub-commands:
    build              Build or rebuild services
    down               Stop all services
    init               Initalize a project
    kill               Kill all running container of the project
    logs               View output from containers
    open               Open a new session inside your dev container
    ps                 List containers
    pull               Pulls service images
    restart            Restart service
    run                Start services and enter in your dev container
    up                 Start all services in detached mode

docky build
------------

Build or rebuild services

Usage:
    docky build [OPTIONS] args...


docky down
-----------

Stop all services

Usage:
    docky down [OPTIONS] args...


docky init
-----------

Initalize a project

Usage:
    docky init [OPTIONS] args...


docky kill
-----------

Kill all running container of the project

Usage:
    docky kill [OPTIONS] args...

Hidden-switches:
    -h, --help      Imprime ce message d'aide et sort


docky logs
-----------

View output from containers

Usage:
    docky logs [OPTIONS] args...


docky open
----------

Open a new session inside the main container or in an specify container if --service is define

Usage:
    docky open [OPTIONS] args...

Meta-options:
    --root                    Open as root

Options:
    --service VALEUR:str      Open the choosen service


docky ps
---------

List containers

Usage:
    docky ps [OPTIONS] args...


docky pull
-----------

Pulls service images

Usage:
    docky pull [OPTIONS] args...


docky restart
--------------

Restart service

Usage:
    docky restart [OPTIONS] args...


docky run
---------

Start services and enter in your dev container

Usage:
    docky run [OPTIONS] args...

Hidden-switches:
    --root                    Run as root

Options:
    --service VALEUR:str      Run the choosen service


docky up
--------

Start all services in detached mode

Usage:
    docky up [OPTIONS] args...
