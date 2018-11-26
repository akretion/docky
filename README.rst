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

The configuration file is in your home : '~/.docky/config.yml'

verbose [True, False]:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Verbose mode is activated by default in order to help you to learn what docky do


env [dev, prod, preprod]:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify which kind of environment is used

network
~~~~~~~~~~~
Docker network configuration for all container run with docky
See docker configuration

proxy
~~~~~~
Proxy configuration:

  - autostart: automatically start proxy when running the container
  - custom_image: custom image name if needed
  - name: name of the proxy container


Automatic Proxy
---------------

When doing dev, is quickly a mess to manage the port of your container, docky integrate a proxy (a basic docker image : https://github.com/akretion/docky-proxy/)

If you want to enjoy this proxy you need to configure a wildcard domain to *.dy to the IP 172.30.0.2

For that on mac and linux system you can install and configure dnsmasq

For Ubuntu (dnsmasq)
~~~~~~~~~~~~~~~~~~~~~~~

Install dnsmasq
```
sudo apt-get install dnsmasq
```

Then configure dnsmasq y adding the line "address=/dy/172.30.0.2" in "/etc/dnsmasq.conf"

Restart it

```
sudo systemctl restart dnsmasq
```

If you have some issue on ubutnu 18.04 please take a look here for the configuration

- https://computingforgeeks.com/install-and-configure-dnsmasq-on-ubuntu-18-04-lts/
- https://superuser.com/questions/1318220/ubuntu-18-04-disable-dnsmasq-base-and-enable-full-dnsmasq

editing the /etc/systemd/resolved.conf and setting "DNSStubListener=no" seem to be the simpliest solution


For Mac (dnsmasq)
~~~~~~~~~~~~~~~~~~~

Google is your friend by some link found, please share the doc you have found

https://passingcuriosity.com/2013/dnsmasq-dev-osx/
https://www.computersnyou.com/3786/how-to-setup-dnsmasq-local-dns/


For Windows (Acrylic DNS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dnsmasq is not available on windows but you can use Acrylic DNS to do exactly the same thing.
See answer here: https://stackoverflow.com/questions/138162/wildcards-in-a-windows-hosts-file?answertab=votes#tab-top


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
