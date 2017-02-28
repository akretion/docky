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

READ the documentation: [Voodoo documentation](http://akretion.github.io/voodoo/master/index.html)
