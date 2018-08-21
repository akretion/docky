Introduction
=================

Odoo dockerized.

> For beginners: get an odoo instance without effort

> For developers: reproductible odoo environments


How it works
---------------

Docky leverage Docker-compose for odoo.

In your **host** run **docky** commands to bootstrap the project and launch docker.

Then in your **guest** (container), run **ak** commands to update odoo dependencies (odoo modules), trigger update scripts and restart odoo server.


Automatic DNS resolution
--------------------------

Docky include an automatic dns resolution by updating your /etc/hosts file and also includ an automatic nginx proxy.
When you run a project in a directory called "my_project" a dns entry will be automatically created and be accessible from the host with my_project.dy. 
As nginx proxy is automatically updated you do not need to specify any port to access to your application.

If you add some plugin (like mailcatcher, pgadmin4 ...). They will be accessible to "my_plugin.my_project.dy"

When you start a app with docky run docky will automatically show the dns available

Getting Started
------------------

Create a new project

.. code-block:: shell

    docky new my_project

Enter in the project directory then run docky

.. code-block:: shell

   cd my_project
   docky run

It will run a new docker image with odoo and postgres inside.


Now let's start Odoo

First run ak build to build you project with anybox buildout recipe

.. code-block:: shell

   ak build

Then launch odoo cmd line to run odoo

.. code-block:: shell

   odoo

Go to http://my_project.dy Odoo is here !

Your databases are also persisted in your repo folder in the .db hidden folder. 
But you can always trash all project databases by simply removing that folder.
