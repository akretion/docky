Introduction
=================

Odoo dockerized.

> For beginners: get an odoo instance without effort

> For developers: reproductible odoo environments


How it works
---------------

Voodoo leverage Docker-compose and `Anybox's buildout <http://pythonhosted.org/anybox.recipe.openerp/>`_ for odoo.

In your **host** run **voodoo** commands to bootstrap the project and launch docker.

Then in your **guest** (container), run **ak** commands to update odoo dependencies (odoo modules), trigger update scripts and restart odoo server.


Automatic DNS resolution
--------------------------

Voodoo includ an automatic dns resolution by updating your /etc/hosts file and also includ an automatic nginx proxy.
When you run a project in a directory called "my_project" a dns entry will be automatically created and be accessible from the host with my_project.vd. As nginx proxy is automatically updated you do not need to specify any port to access to your application.

If you add some plugin (like mailcatcher, pgadmin4 ...). They will be accessible to "my_plugin.my_project.vd"

When you start a app with voodoo run voodoo will automatically show the dns available

Getting Started
------------------

Create a new project

.. code-block:: shell

    voodoo new my_project

Enter in the project directory then run voodoo

.. code-block:: shell

   cd my_project
   voodoo run

It will run a new docker image with odoo and postgres inside.


Now let's start Odoo

First run ak build to build you project with anybox buildout recipe

.. code-block:: shell

   ak build

Then launch ak run to start odoo

.. code-block:: shell

   ak run

Go to http://my_project.vd Odoo is here !


Another usage
-------------------

Use as a simple Odoo project repository managed by Anybox recipe (without using Docker)

You can clone a voodoo branch to start your project as simple convenience repo for your project. With the buildout.cfg file you can pin exactly your shared branches dependencies. You also keep the project specific modules under revision control in the modules folder.

For further details, please simply refer to `Anybox recipe documentation <http://docs.anybox.fr/anybox.recipe.openerp/trunk>`_


Note that the Docker workdir is your repo that is shared with Docker, so you won't loose your source changes nor loose time copying files.

Your databases are also persisted in your repo folder in the .db hidden folder. But you can always trash all project databases by simply removing that folder.
