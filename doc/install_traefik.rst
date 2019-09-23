Install traefik (1.7)
=======================

Download traefik binary

.. code-block:: shell

    sudo curl -L https://github.com/containous/traefik/releases/download/v1.7.11/traefik_linux-amd64 -o /usr/bin/traefik
    sudo chmod 755 /usr/bin/traefik


Add systemd configuration in /etc/systemd/system/traefik.service

.. code-block:: shell

    sudo curl https://raw.githubusercontent.com/akretion/docky/master/traefik/traefik.service -o /etc/systemd/system/traefik.service

Add traefik configuration at /etc/traefik/traefik.toml (create missing directory before)

.. code-block:: shell

    sudo mkdir /etc/traefik
    sudo curl https://raw.githubusercontent.com/akretion/docky/master/traefik/traefik.toml -o /etc/traefik/traefik.toml

Create specific user

.. code-block:: shell

    sudo useradd -G docker -r -s /bin/false -U -M traefik

Start traefik automatically

.. code-block:: shell

    sudo systemctl enable traefik


Traefik Labels
------------------

Now you have traefik running you need to add a label to your container (to route a domain with traefik)

Odoo Example
~~~~~~~~~~~~~~

.. code-block:: shell

    traefik.longpolling.frontend.rule: "Host:my-project.localtest.me;PathPrefix:/longpolling/"
    traefik.longpolling.port: 8072
    traefik.www.frontend.rule: "Host:my-project.localtest.me"

Will route the domain my-project.dy to your odoo container


Wagon Example
~~~~~~~~~~~~~~

.. code-block:: shell

    traefik.wagon.frontend.rule: "Host:my-project.localtest.me"
    traefik.wagon.port: 3333

Will route the domain my-project.localtest.me to your wagon container

more information here : https://docs.traefik.io/configuration/backends/docker/#on-containers


Route your domain to traefik IP
--------------------------------

In the example we use a public dns configuration that resolve *whatever*.localtest.me to 127.0.0.1
It's a cool solution for quick demo but we do not recommand to use external dns (that can be hacked and you may be redirected on somewhere else)

The simpliest solution is to use you own domain like "my-project.dy" and then in /etc/hosts to add 127.0.0.1 my-project.dy

If you want automatic wildcard dns resolution *whatever*.dy then: `Install Dnsmasq <https://github.com/akretion/docky/blob/master/doc/install_dnsmasq.rst>`



Optionnal Additionnal Docky Labels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The label docky.access.help is an helper that print the url when starting the container

_.. code-block:: shell

    docky.access.help: http://mycustomer.dy/mystuff

Will show the following help when starting the container

.. code-block:: shell

    The service odoo is accessible on http://mycustomer.dy/mystuff
