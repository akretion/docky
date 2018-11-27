Introduction
=================

Odoo dockerized.

> For beginners: get an odoo instance without effort

> For developers: reproductible odoo environments


How it works
---------------

Firtsly, we will pull a blank odoo template from github and create it on our hard drive.

We will build it and run it to have a functional odoo project. 
 
In odoo/spec.yaml, you will find module's url from github that you want to install when you build your odoo project. 

In odoo/requirements.txt, you will find all python dependency you need to run your odoo project.

In dev.docker-compose.yml, you will find the global configuration of your odoo project.
You can change the database name, add path for all addons and more for example. 

Automatic DNS resolution
--------------------------

Docky includ an automatic dns resolution by updating your /etc/hosts file and also includ an automatic nginx proxy.
When you run a project in a directory called "my_project" a dns entry will be automatically created and be accessible from the host with my_project.vd. As nginx proxy is automatically updated you do not need to specify any port to access to your application.

If you add some plugin (like mailcatcher, pgadmin4 ...). They will be accessible to "my_plugin.my_project.vd"

When you start a app with docky run docky will automatically show the dns available

Getting Started
------------------

Create a new project

.. code-block:: shell

    git clone 'template's github url' -b 'branch's name' 'directory's name'

Enter in the project directory then ak build

.. code-block:: shell

   cd 'directory's_name'
   directory's_name$ ak build

It will run a new docker image with odoo and postgres inside. after this go out of the directory with cd ..


Now let's start Odoo

First run docky build to build you project with anybox buildout recipe, then run it.

.. code-block:: shell

   docky build
   docky run

Then launch odoo

.. code-block:: shell

   odoo

Go to http://directory's_name.dy Odoo is here !


Another usage
-------------------

Use as a simple Odoo project repository managed by Anybox recipe (without using Docker)

You can clone a docky branch to start your project as simple convenience repo for your project. With the buildout.cfg file you can pin exactly your shared branches dependencies. You also keep the project specific modules under revision control in the modules folder.

For further details, please simply refer to `Anybox recipe documentation <http://docs.anybox.fr/anybox.recipe.openerp/trunk>`_


Note that the Docker workdir is your repo that is shared with Docker, so you won't loose your source changes nor loose time copying files.

Your databases are also persisted in your repo folder in the .db hidden folder. But you can always trash all project databases by simply removing that folder.
