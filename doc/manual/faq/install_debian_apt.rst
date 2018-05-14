Install custom debian package
================================

If you need some custom debian package in your image you can easily add one using a Dockerfile see documentation here : https://docs.docker.com/engine/reference/builder/

Here is an example of custom DockerFile to install the package "my_debian_package_to_install".
Be careful to not forget to switch the user before and after installing the package.

.. code-block:: shell

    FROM akretion/docky:latest
    USER root
    RUN DEBIAN_FRONTEND=noninteractive && \
        apt-get update && \
        apt-get install -y my_debian_package_to_install && \
        apt-get clean
    USER odoo

Then you need to replace the following information in your dev.docker-compose.yml and docker-compose.yml

.. code-block:: shell

    image: akretion/docky:latest

By

.. code-block:: shell

    build: .

Then

.. code-block:: shell

    docky build

to build a custom image
