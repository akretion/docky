## Welcome to Voodoo

Some black magic for your Odoo projects! With Voodoo, it is you who controls the Odoo, not the reverse ;-)

[![Voodoo by Akretion](https://s3.amazonaws.com/akretion/assets/voodoo.png)](http://akretion.com)

### Quick start on Ubuntu

Install or upgrade your Docker:
```
  curl -sSL https://get.docker.io/ubuntu/ | sudo sh
```

Give non root access to Docker if not done already:
```
  sudo gpasswd -a ${USER} docker
  sudo service docker restart # use docker.io instead of docker in Ubuntu 14.04
```

**you may have to LOGOUT and LOG BACK IN AGAIN for the group change to take effect!**

A simple test to see if you have non root access is to list your docker images with
```
   docker images # make sure you don't need sudo anymore here
```

Create a new Voodoo project (you could also clone an existing one from elsewhere)
```
  git clone https://github.com/akretion/voodoo.git
  cd voodoo
```

If you already have a local odoo 8.0 repo on your computer on the proper branch,
adjust the path of odoo-directory (by default ~/.buildout/odoo8) in the buildout.dev.cfg file!
You can eventually create a symbolic link at ~/.buildout/odoo8 pointing to an existing local repo.

We will now step into a Docker container able to run Odoo.
Warning, the first time it will download the akretion/voodoo image of 1.6 GB!
```
  ./ak
  ak run  # (inside the container)
```

### How it works

Firstly Voodoo is a **template repository** to clone and use as a seed for all your Odoo projects. Because it's based on the Anybox recipe 'de facto standard', it allows you to keep under git revision control, all your project branch dependencies (via the buildout.cfg file ) and your project specific modules (in the modules folder). Once you do that, your project becomes easy to share with any developer.

Secondly Voodoo comes with a **complete development runtime**, with all compiled Python dependencies (for v7, v8 and master) and a disposable Postgresql server. It allows to very quickly fire up a new development server that closely matches the production without clutering your shinny but small computer SSD disk with stale dependencies all over the place.

Because it uses Docker, it's very fast and lightweight. You'll never again find yourself unwilling to fix an old customer bug because the cost to setup a dev server is too high. Voodoo is also based on Devstep by Fabio Rehm.

Best of all, new comers can even play with it on Windows!

**WARNING** Voodoo is **NOT designed for production**: running user has too much privileges and database setup isn't for production.


### Usages

So several usages are possible: from the Odoo project repository to a complete development server for your platform. Please read the section that matches your use case!

## Use as a simple Odoo project repository managed by Anybox recipe (without using Docker)

You can clone a voodoo branch to start your project as simple convenience repo for your project. With the buildout.cfg file you can pin exactly your shared branches dependencies. You also keep the project specific modules under revision control in the modules folder.

For further details, please simply refer to [Anybox recipe documentation](http://docs.anybox.fr/anybox.recipe.openerp/trunk/)


## Use as a disposable Docker hackable development server on Linux

See Quickstart on Ubuntu session for details.

From the host or from inside the container, available ak commands are:

```
  ./ak [up|run|build] [Odoo args]
```

* **ak up**: build the project with bin/buildout and run the server connected to a convenient embeded Postgresql server
* **ak run**: simply run the development server without rebuilding it
* **ak build**: build the server with buildout and the recipe and open a shell where you can decide what you will do next
* **ak psql**: connect to the default db database in console mode
* **ak**: without arguments, ak will just step into the development container and let you hack from there in a shell

any extra arguments you'll pass after the ak command will be forwarded to the Odoo server (for instance ak run -i demo_module will install the demo module).

Note that the Docker workdir is your repo that is shared with Docker, so you won't loose your source changes nor loose time copying files.

Your databases are also persisted in your repo folder in the .db hidden folder. But you can always trash all project databases by simply removing that folder.

## Extra feature

If you need a graphical interface for exploring the database then just add the following line into you .bashrc configuration file

```sh
export USE_ADMINER=true
```


## Use on Windows, Mac OS X or Linux with Vagrant + Docker

Voodoo can run anywhere Vagrant and Docker can run, that is even on Windows and MacOSX thanks to boot2docker.

* First install [a recent version of Vagrant](from http://www.vagrantup.com/downloads.html).
* And also install [Virtualbox](https://www.virtualbox.org/wiki/Downloads) unless you are on Linux with Docker installed.

Simply do:

```
  vagrant up; vagrant docker-logs --follow
```

If you touch you source files, you can reload the server with:

```
  vagrant reload
```

You can destroy the container when you don't need it anymore with:

```
  vagrant destroy -f
```

## Troubleshooting

[See Troubleshooting in the wiki](https://github.com/akretion/voodoo/wiki/Troubleshooting)

## Roadmap
- udpate/fix documentation
- add pre-copy of odoo repo in background for generating quickly a new project
