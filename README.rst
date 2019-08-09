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


Installation and Update
-------------------------

You need to install docker-ce : https://docs.docker.com/install/

Then install docky with python3

.. code-block:: shell

    sudo pip3 install docky

Update Docky:
------------------

.. code-block:: shell

    sudo pip3 install docky --upgrade


Configuration:
--------------

Bootstrap a project with :

.. code-block:: shell
    docky init


Automatic Proxy
---------------

Introduction
~~~~~~~~~~~~~~~~~

When doing dev, is quickly a mess to manage the port of your container

Previous version of docky was including a proxy based on nginx docker image.
This solution was adding some restriction (like using the same network for all container)
Now we recommands to simply install traefik and dns resolver like dnsmasq on your host.

Dnsmasq will resolve all *.dy* domain to your localhost 127.0.0.1

Traefik will route the domain name my-customer.dy to the container of your customer



Install traefik (1.7)
~~~~~~~~~~~~~~~~~~~~~~~~~

Download traefik binary

.. code-block:: shell
    sudo curl https://github.com/containous/traefik/releases/download/v1.7.11/traefik_linux-amd64 -o /usr/bin/traefik
    sudo chmod 755 /usr/bin/traefik


Add systemd configuration in /etc/systemd/system/traefik.service

.. code-block:: shell

    sudo curl https://raw.githubusercontent.com/akretion/docky/master/traefik/traefik.service -o /etc/traefik/traefik.service

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


Install Dnsmasq (For Ubuntu 18.04)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1 Install dnsmasq with apt
_______________________________

.. code-block:: shell

    sudo apt-get install dnsmasq-base

Note : You just need to install the base package, you can uninstall dnsmasq package if installed by error

2 Unactive systemd-resolve dns
____________________________________

Edit /etc/systemd/resolved.conf and set "DNSStubListener=no"

.. code-block:: shell

    # See resolved.conf(5) for details

    [Resolve]
    #DNS=
    #FallbackDNS=
    #Domains=
    #LLMNR=no
    #MulticastDNS=no
    #DNSSEC=no
    #Cache=yes
    DNSStubListener=no   #<---- add this line here


then restart :



.. code-block:: shell

    systemctl restart systemd-resolved

3 Enable and configure dnsmasq in NetworkManager
__________________________________________________

Edit the file /etc/NetworkManager/NetworkManager.conf, and add the line dns=dnsmasq to the [main] section, it will look like this:

.. code-block:: shell

    [main]
    plugins=ifupdown,keyfile
    dns=dnsmasq       #<---- just add this line

    [ifupdown]
    managed=false

    [device]
    wifi.scan-rand-mac-address=no


Let NetworkManager manage /etc/resolv.conf

.. code-block:: shell

    sudo rm /etc/resolv.conf ; sudo ln -s /var/run/NetworkManager/resolv.conf /etc/resolv.conf

Configure dy (add a .dy wildcard to localhost 127.0.0.1)

.. code-block:: shell
    echo 'address=/.dy/127.0.0.1' | sudo tee /etc/NetworkManager/dnsmasq.d/dy-wildcard.conf


Reload NetworkManager

.. code-block:: shell

    sudo systemctl reload NetworkManager


inspired from :
https://askubuntu.com/questions/1029882/how-can-i-set-up-local-wildcard-127-0-0-1-domain-resolution-on-18-04


For Mac (dnsmasq)
~~~~~~~~~~~~~~~~~~~

Google is your friend by some link found, please share the doc you have found

https://passingcuriosity.com/2013/dnsmasq-dev-osx/
https://www.computersnyou.com/3786/how-to-setup-dnsmasq-local-dns/


For Windows (Acrylic DNS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dnsmasq is not available on windows but you can use Acrylic DNS to do exactly the same thing.
See answer here: https://stackoverflow.com/questions/138162/wildcards-in-a-windows-hosts-file?answertab=votes#tab-top

Service Labels
-----------------
Labels are used by docky and traefik.

Traefik Labels
~~~~~~~~~~~~~~~

.. code-block:: shell
    traefik.frontend.rule: Host:mycustomer.dy

Will route the domain mycustomer.dy to your container
more information here : https://docs.traefik.io/configuration/backends/docker/#on-containers

Docky Labels
~~~~~~~~~~~~~

.. code-block:: shell
    docky.access.help: http://mycustomer.dy/mystuff

Will show the following help when starting the container

.. code-block:: shell
    The service odoo is accessible on http://mycustomer.dy/mystuff


The label docky.main.service and docky.user

.. code-block:: shell
    docky.main.service: odoo
    docky.user: odoo

Allow to define the main service of your docker compose and the user that should be user to enter in the container

Getting Started
---------------------

Use docky --help

But basically docky run is your friend

READ the documentation: `Docky documentation <http://akretion.github.io/docky/master/index.html>`_


Troubleshooting
--------------------

To avoid issue with line wrapping with "docky open" please use a version of docker > to  18.06.0-ce
see : https://github.com/docker/compose/issues/6151

Other issue :
see https://github.com/akretion/docky/wiki

Changelog
----------

version 7.0.0

- remove the need of docky config file in $HOME
- use .env to be more compatible with docker-compose
- improve templates
- create init command
- heavy refactoring


version 6.0.0

- refactor remove proxy code and use traefik
- remove docky.yml now you must use labels on services (see doc)
- add option "--service=myservice" on docky run and docky open

version 5.0.0:

- Resolve mac compatibility by remove proxy code that use a mounted version of etc/hosts
  now you need to install dnsmasq.
  This should also solve windows compatibilty by using the local dns https://stackoverflow.com/questions/138162/wildcards-in-a-windows-hosts-file?answertab=votes#tab-top
- Solve issue with project name in multi user env (the name is based on user + directory name)
- Add possibility to specify the service for run, open, logs, kill, down, restart, start cmd
  for example now you can do "docky open db" to open a terminal on the db server
  or you can restart a service like "docky restart varnish"
- Solve issue with missing aliases name
- Solve issue with missing environment variable with docky open (now we use a monkey-pacthed version of docker-compose exec)
- Fix documentation build
- Improve docky none specific cmd to a project to be run without project.
  For example, you can use docky help, docky proxy outside of a directory project
