## Voodoo

Odoo dockerized.

> For beginners: get an odoo instance without effort

> For developers: reproductible odoo environments 


[![Voodoo by Akretion](https://s3.amazonaws.com/akretion/assets/voodoo.png)](http://akretion.com)


### How it works

Voodoo leverage Docker-compose and  [Anybox's buildout](http://pythonhosted.org/anybox.recipe.openerp/) for odoo.

In your __host__ run __voodoo__ commands to bootstrap the project and launch docker.

Then in your __guest__ (container), run __ak__ commands to update odoo dependencies (odoo modules), trigger update scripts and restart odoo server.



###  Getting Started

Create a new project

```
    voodoo new my_project
```

Enter in the project directory then run voodoo

```
   cd my_project
   voodoo run
```
It will run a new docker image with odoo and postgres inside.


Now let's start Odoo

First run ak build to build you project with anybox buildout recipe
```
   ak build
```

Then launch ak run to start odoo
```
   ak run
```

Go to http://localhost:8069 Odoo is here !


### Install on Ubuntu

#### Prerequisite

* You need a 64 bits architecture.
* You will need to install the Python development headers (python-dev)
* Your user needs to have system uid = 1000  (known issue)


#### Install or upgrade your Docker:


```
wget -qO- https://get.docker.com/ | sh
```

More information on the installation on https://docs.docker.com/v1.6/installation/ubuntulinux/
in the section Docker-maintained Package Installation.

Please do not forget to install the latest version if you choose to install it manually


* Give non root access to Docker if not done already:
```
  sudo gpasswd -a ${USER} docker
  sudo service docker restart # use docker.io instead of docker in Ubuntu 14.04
```

**you may have to LOGOUT and LOG BACK IN AGAIN for the group change to take effect!**

* A simple test to see if you have non root access is to list your docker images with
```
   docker images # make sure you don't need sudo anymore here
```


#### Install Voodoo:

```
  sudo pip install git+https://github.com/akretion/voodoo.git --upgrade
```



### Voodoo Command

Voodoo extends docker-compose so it can do everything docker-compose can do. For more information about extra commands you can read the docker-compose documentation: http://docs.docker.com/compose


#### voodoo new
will bootstrap a new project by cloning a default project template.

#### voodoo run
will run your project and give you a bash session directly in the odoo container

#### voodoo open
will open a new session to an existing running container. 

For example you may need a first terminal for running odoo and a second terminal for doing some psql. 


#### List of all command

```
voodoo 1.0

Usage:
    voodoo [SWITCHES] [SUBCOMMAND [SWITCHES]] args...

Meta-switches
    -h, --help         Prints this help message and quits
    --help-all         Print help messages of all subcommands and quit
    -v, --version      Prints the program's version and quits

Switches
    --dry-run          Dry run mode
    --verbose          Verbose mode

Subcommands:
    build              Build or rebuild services
    kill               Kill all running container of the project
    logs               View output from containers
    new                Create a new project
    open               Open a new session inside your dev container
    ps                 List containers
    pull               Pulls service images
    run                Start services and enter in your dev container
    start              Start services
    stop               Stop services
```


### ak Command
See ak help : https://github.com/akretion/ak


### Project customizations

Important files are 
* __buildout.cfg__, 
* __buildout.dev.cfg__, 
* __docker-compose.yml__
* __dev.docker-compose.yml__

More information about buildout files are available [here](http://pythonhosted.org/anybox.recipe.openerp/)


#### Config.yml
For now there is two option for you default config

__shared_eggs__ [True or False]: If true the ~/.voodoo/shared/eggs will be mounted as eggs folder in your docker
This mean that the eggs will be shared between your voodoo projects saving some download and space.

If you don't want share eggs for a specific project, just create your `./eggs` folder after created your project (voodoo new).

odoo [url]: The odoo repo by default the  OCA repo: 'https://github.com/oca/ocb.git'

If you want start your project quickly and avoid to duplicate odoo source code, you can create manually a symbolic link after  created project in `./parts/odoo` from existing odoo projects.

  Sharing source can be confusing, don't use for dev of projects which are in production.

Note : to improve the performance when downloading odoo, an odoo project is downloaded in ~/.voodoo/shared/odoo. Then when you start a new project the new odoo part is created from this local repository.

### FAQ

see wiki https://github.com/akretion/voodoo-cli/wiki


### Other apps available
pgcli

[![Pgcli](https://github.com/amjith/pgcli/raw/master/screenshots/image02.png)](https://github.com/amjith/pgcli)


### Another usage
Use as a simple Odoo project repository managed by Anybox recipe (without using Docker)

You can clone a voodoo branch to start your project as simple convenience repo for your project. With the buildout.cfg file you can pin exactly your shared branches dependencies. You also keep the project specific modules under revision control in the modules folder.

For further details, please simply refer to [Anybox recipe documentation](http://docs.anybox.fr/anybox.recipe.openerp/trunk/)


Note that the Docker workdir is your repo that is shared with Docker, so you won't loose your source changes nor loose time copying files.

Your databases are also persisted in your repo folder in the .db hidden folder. But you can always trash all project databases by simply removing that folder.

## Roadmap
- udpate/fix documentation
- add pre-copy of odoo repo in background for generating quickly a new project (mv .odoocache)
- review voodoo new (maybe it will better to have a template folder un voodoo cli)
- share vim info...
- generate automatically ssh key if missing
- debian package
- add bash completion
- add dynamic port
