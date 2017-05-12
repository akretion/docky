Install on Ubuntu
====================

Prerequisite
---------------

* You need a 64 bits architecture.
* You will need to install the Python development headers (python-dev)
* You will need to install the Python package manager PIP

Install or upgrade your Docker:
----------------------------------

Please go to docker documentation installation page : `Install Docker
<https://docs.docker.com/engine/installation>`_

* Give non root access to Docker if not done already:

.. code-block:: shell

  sudo gpasswd -a ${USER} docker
  sudo service docker restart

**you may have to LOGOUT and LOG BACK IN AGAIN for the group change to take effect!**

* A simple test to see if you have non root access is to list your docker images with

.. code-block:: shell

   docker images # make sure you don't need sudo anymore here


Install Voodoo:
------------------

.. code-block:: shell

    sudo pip install voodoo-cli
    
Update Voodoo:
------------------

.. code-block:: shell

    sudo pip install voodoo-cli --upgrade
    docker pull akretion/voodoo

Configuration:
--------------

The configuration file is in your home : '~/.voodoo/config.yml'

verbose [True, False]:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Verbose mode is activated by default in order to help you to learn what voodoo do


env [dev, prod, preprod]:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify which kind of environment is used

maintainer_quality_tools [url]:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

URL for the maintainer-quality-tools of OCA used for testing the code

shared_eggs [True or False]:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If true the ~/.voodoo/shared/eggs will be mounted as eggs folder in your docker
This mean that the eggs will be shared between your voodoo projects saving some download and space.

If you don't want share eggs for a specific project, just create your `./eggs` folder after created your project (voodoo new).

shared_gems [True or False]:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If true the ~/.voodoo/shared/gems will be mounted as gems folder in your docker
This mean that the gems will be shared between your voodoo projects saving some download and space.

odoo [url]:
~~~~~~~~~~~~

The odoo repo by default the  OCA repo: 'https://github.com/oca/ocb.git'

If you want start your project quickly and avoid to duplicate odoo source code, you can create manually a symbolic link after  created project in `./parts/odoo` from existing odoo projects. Sharing source can be confusing, don't use for dev of projects which are in production.

Note : to improve the performance when downloading odoo, an odoo project is downloaded in ~/.voodoo/shared/odoo. Then when you start a new project the new odoo part is created from this local repository.
