Install Dnsmasq
====================

For Ubuntu 18.04
~~~~~~~~~~~~~~~~~~

1 Install dnsmasq with apt
----------------------------

.. code-block:: shell

    sudo apt-get install dnsmasq-base

Note : You just need to install the base package, you can uninstall dnsmasq package if installed by error

2 Unactive systemd-resolve dns
----------------------------------

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
--------------------------------------------------

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

S
