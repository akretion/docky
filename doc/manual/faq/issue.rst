Issue help
============

What should I do if I have this message after ```voodoo run```
------------------------------------------------------------------

.. image:: https://cloud.githubusercontent.com/assets/1853434/6959305/b73aaec4-d917-11e4-9f45-00d1332901a2.png

Something wrong have occured with your docker server please run

.. code-block:: shell

    sudo service docker.io restart


What process manage my voodoo container ?
--------------------------------------------

.. code-block:: shell

    voodoo ps

to kill your all process use

.. code-block:: shell

    voodoo kill

What do to if you have this stack trace?
--------------------------------------------

.. code-block:: shell

    Renato:  renato@renato-ultrabook:~$ voodoo new project
    Traceback (most recent call last):
     File "/usr/local/bin/voodoo", line 5, in <module>
       from pkg_resources import load_entry_point
     File "/usr/local/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3074, in <module>
       @_call_aside
     File "/usr/local/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3060, in _call_aside
       f(*args, **kwargs)
     File "/usr/local/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 3087, in _initialize_master_working_set
       working_set = WorkingSet._build_master()
     File "/usr/local/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 647, in _build_master
       return cls.build_from_requirements(__requires_)
     File "/usr/local/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 660, in _build_from_requirements
       dists = ws.resolve(reqs, Environment())
     File "/usr/local/lib/python2.7/dist-packages/pkg_resources/__init__.py", line 833, in resolve
       raise DistributionNotFound(req, requirers)
    pkg_resources.DistributionNotFound: The 'requests<2.6,>=2.2.1' distribution was not found and is required by docker-compose

The best is you update your docker-compose egg with:

.. code-block:: shell

    sudo pip install docker-compose -U

and try again.
