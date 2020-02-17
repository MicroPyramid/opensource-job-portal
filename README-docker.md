# Managing your docker deployed site

**Note:** This documentation is intentionally generic so that it can
be copy-pasted between projects - do not put project specific details here.

This document explains how to do various sysadmin related tasks when your
site has been deployed under docker. Three deployment modes are supported:

* **production**: no debug etc is enabled, has its own discrete database. Configure
  your production environment in jobsp.settings_server - this
  DJANGO_SETTINGS_MODULE is used when running in production mode.
* **development**: Configure your development environment in jobsp.settings_server -
  this DJANGO_SETTINGS_MODULE is used when running in production mode. Please see
  README-dev.md for more information on setting up a developer environment.

**Note:** We really recommend that you use docker 1.8 or greatr so that you
  can take advantage of the exec command as well as other newer features.

## Build your docker images and run them

### Production

You can simply run the provided Makefile commands and it will build and deploy the docker
images for you in **production mode**.

```
cd deployment
# make commands coming soon ...
make build
make permissions
make web
# Wait a few seconds for the DB to start before to do the next command
make migrate
make collectstatic
```

#### Using make

Using the make commands is probably simpler - the following make commands are
provided for production (you can obtain this list by typing ``make help`. All commands
should be run from in the ``deployment`` directory.


* **build** - builds all required containers.
* **build-devweb** - build the development container. See [development notes](README-dev.md).
* **collectstatic** - run the django collectstatic command.
* **create-machine** .
* **db** - build and run the db container.
* **dbbackup** - make a snapshot of the database, saving it to deployments/backups/YYYY/MM/project-DDMMYYYY.dmp. It also creates a symlink to backups/latest.dmp for the latest backup.
* **dbbash** - open a bash shell inside the database container.
* **dblogs** - view the database logs.
* **dbrestore** - restore deployment/backups/latest.dmp over the active database. Will delete any existing data in your database and replace with the restore, so **use with caution**.
* **dbschema** - dump the current db schema (without data) to stdio. Useful if you want to compare changes between instances.
* **dbshell** - get a psql prompt into the db container.
* **dbsnapshot** - as above but makes the backup as deployment/snapshot.smp - replacing any pre-existing snapshot.
* **dbsync** - use this from a development or offsite machine. It will rsync all database backups from deployment/backups to your offsite machine.
* **default** .
* **deploy** .
* **devweb** - create an ssh container derived from uwsgi that can be used as a remote interpreter for PyCharm. See [development notes](README-dev.md).
* **enable-machine** -
* **kill** - kills all running containers. Does not remove them.
* **logs** - view the logs of all running containers. Note that you can also view individual logs in the deployment/logs directory.
* **mailerrorlogs** - View the error logs from the mail server.
* **maillogs** - view the transaction logs from the mail server.
* **mediasync** - use this from a development or offsite machine. It will rsync all media backups from deployment/media to your offsite machine.
* **migrate** - run any pending migrations.
* **nginx** - builds and runs the nginx container.
* **nginxlogs** - view just the nginx activity logs.
* **permissions** - Update the permissions of shared volumes. Note this will destroy any existing permissions you have in place.
* **reload** - reload the uwsgi process. Useful when you need django to pick up any changes you may have deployed.
* **rm** - remove all containers.
* **rm-only** - remove any containers without trying to kill them first.
* **run** - builds and runs the complete orchestrated set of containers.
* **sentry** - **currently not working I think.** The idea is to spin up a sentry instance together with your app for fault reporting.
* **shell** - open a bash shell in the uwsgi (where django runs) container.
* **superuser** - create a django superuser account.
* **update-migrations** - freshen all migration definitions to match the current code base.
* **web** - same as **run** - runs the production site.


e.g. ``make web``

#### Arbitrary commands

Running arbitrary management commands is easy (assuming you have docker >= 1.3)
e.g.:

```
docker exec foo_web_1 /usr/local/bin/python /home/web/django_project/manage.py --help
```

**Note:** rm should not destroy any data since it only removes containers
and not host volumes for db and django. All commands should be non-destructive
to existing data - though **smart people make backups before changing things**.


## Setup nginx reverse proxy

You should create a new nginx virtual host - please see
``*-nginx.conf`` in the deployment directory of the source for an example.

Simply add the example file (symlinking is best) to your ``/etc/nginx/sites-enabled/`` directory
and then modify the contents to match your domain. Then use

```
sudo nginx -t
```

To verify that your configuration is correct and then reload / restart nginx
e.g.

```
sudo /etc/init.d/nginx restart
```

**Note that the default configuration runs the service directly on port 80 since
we assume there is a dedicated server for deployment.**

# Configuration options

You can configure the base port used and various other options like the
image organisation namespace and postgis/mysql user/pass by editing the ``docker-compose.yml``
files.
