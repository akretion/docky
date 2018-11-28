Introduction
=================

Odoo dockerized.

> For beginners: get an odoo instance without effort

> For developers: reproductible odoo environments


How it works
---------------

Firtsly, we will pull a blank odoo template from github and create it on our hard drive.

We will build it and run it to have a functional odoo project. 
 
In odoo/spec.yaml, you will write module's url from github that you need to install when you build your odoo project. 

In odoo/requirements.txt, you will write all python dependency you need to run your odoo project.

In dev.docker-compose.yml, you will find the global configuration of your odoo project.
This file is not in the blank template by default but if you run docky build, it will ask you if you want to create it. 

Automatic DNS resolution
--------------------------

Docky includ an automatic dns resolution by updating your /etc/hosts file and also includ an automatic nginx proxy.
When you run a project in a directory called "my_project" a dns entry will be automatically created and be accessible from the host with my_project.vd. As nginx proxy is automatically updated you do not need to specify any port to access to your application.

If you add some plugin (like mailcatcher, pgadmin4 ...). They will be accessible to "my_plugin.my_project.vd"

When you start a app with docky run docky will automatically show the dns available

Getting Started
------------------

Clone a new project

.. code-block:: shell

    git clone 'template's github url' -b 'branch's name' 'directory's name'

Enter in the project directory, in odoo directory, then ak build


If you doesn't have `ak <https://github.com/akretion/ak>`_, you can install it with this command : 

.. code-block:: shell

    pip3 install git+https://@github.com/akretion/ak

.. code-block:: shell

   cd 'directory's_name/odoo'
   directory's_name/odoo$ ak build


Ak build will use the file requirements.txt and spec.yaml to generate theses directory in the odoo directory : 'external-src', 'links' and 'src'.

After this ak build ;

-> Directory 'external-src' contains all the modules you write in the file 'odoo/spec.yaml'. 

-> Directory 'src' contains all modules installed by default in Odoo, all theses modules come from OCB
More informations here : https://github.com/OCA/OCB. 

After this go out of the directory with cd ..


Now let's start Odoo

.. code-block:: shell

   docky build

It will run a new docker image with odoo and postgres inside.
Docky build will read and execute the file 'odoo/Dockerfile'.

If you doesn't have the file 'dev.docker-compose.yml' before the docky build, it will automatically ask you if you want to create the file.

Then, run it.

.. code-block:: shell

   docky run

It will create 4 new differents containers for your odoo web service and your database.
After running docky, you will be in the odoo web service container by default :
odoo@'containers':/$

It will read the file 'directory's_name/odoo/dev.docker-compose.yml'

Then you can start your odoo

.. code-block:: shell

   odoo

It will read the file '/etc/odoo.cfg' and all the module in the path '/odoo/src/odoo'

Go to http://directory's_name.dy Odoo is here !


Another usage
-------------------
 
Your databases are also persisted in your repo folder in the .db hidden folder. But you can always trash all project databases by simply removing that folder.
