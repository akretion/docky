Introduction
=================

docky : Make docker and docker compose simply !


History
----------
This project was initialy created for building odoo environments without effort based on docker-compose and docker

Step by step we make it generic and now we also use it for our rails, ruby developpment

How it works
---------------

Docky is depend on docker-compose and use exactly the same file (so you can move from docker-compose to docky and vice-versa without any effort)

Docky just make docker-compose simplier and integrate a default docker-compose file generator


Automatic Proxy
---------------

When doing dev is quickly a mess to manage the port of your container, docky integrate a proxy (a basic docker image : https://github.com/akretion/docky-proxy/)

That will generate for you a local domain .dy that will make your container accessible, for example with a project call **my customer**: you have a domain **my-customer.dy**


Getting Started
---------------------


READ the documentation: `Docky documentation <http://akretion.github.io/docky/master/index.html>`_


Troubleshooting
--------------------

To avoid issue with line wrapping with "docky open" please use a version of docker > to  18.06.0-ce
see : https://github.com/docker/compose/issues/6151

Other issue :
see https://github.com/akretion/docky/wiki
