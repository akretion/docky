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

Voodoo includ an automatic dns resolution by integrating `resolvable from gliderlabs <https://github.com/gliderlabs/resolvable>`_

When you run a project in a directory called "my_project" a dns entry will be automatically created and be accessible from the host with my_project.vd


Getting Started
---------------------

READ the documentation: `Voodoo documentation <http://akretion.github.io/voodoo/master/index.html>`_
