# Developer Documentation

**Note:** This documentation is intentionally generic so that it can
be copy-pasted between projects - do not put project specific details here.

## Application architecture under docker

The following diagram provides and overview of the core architecture
components (Database, uwsgi server, web server):

![dockerdjangoarchitecture - new page 1](https://cloud.githubusercontent.com/assets/178003/5024388/750b85c8-6b12-11e4-97b0-c73b2d07e539.png)


The blue box is there to provide a means to develop on the same environment
as you deploy and would not be relevant for server side deployments.
Everything is managed using docker containers, with pycharm
making ssh connections into the developer container and using the
python interpreter found therein. Newer versions of PyCharm have 'native' docker support
but after testing we opted to continue to use the ssh method described here. You may want to
test when new versions of PyCharm come out in case they have improved the direct docker support.

**Note:** You don't need to use this architecture, you can deploy as a standard
django app using virtualenv and locally installed postgis/mysql, nginx etc.

## Setup pycharm to work with a remove docker development environment

### Build and run your dev docker image

This image extends the production one, adding ssh to it. You must
have built the production one first by following the "Quick Installation Guide"!
When it's done, you can continue with this command:

Linux and MacOS:

```
make build-devweb
make devweb
```

Windows:

```
make-devbuild.bat
make-devweb.bat
```

### Create a remote interpreter in pycharm

Open the project in pycharm then do:

* File -> Settings
* Project Interpreter
* Click on the gear icon next to project interpreter
* Add remote...

Now use these credentials:

* SSH Credentials (tick)
* Host: localhost
* Port: (use the ssh port specified in the docker-compose.yml file)
* User name: root
* Auth type: password (and tick 'save password')
* Password: docker
* Python interpreter path: ``/usr/local/bin/python``

When prompted about host authenticity, click Yes.
After the python interpreter is set, set its path mapping:

  * **Local path:** `<path to your git repo>/django_project`
  * **Remote path:** `/home/web/django_project`

After that you should see something like this:
   `<Project root>/django_project→/home/web/django_project`

In settings, django support:

* tick to enable django support.
* Set django project root to the path on your host that holds django code e.g.
  ``<path to code base>/django_project``
* Set the settings option to your setting profile e.g.
  ``jobsp.settings_server``. If you need to use custom settings, copy
  this file e.g. ``jobsp.settings_local.py`` and place your modifications in your
  personalised copy. The first import of your custom file should import from
  jobsp.settings_server.

* manage script (leave default)


### Create the django run configuration

* Run -> Edit configurations
* Click the `+` icon in the top left corner
* Choose ``Django server`` from the popup list

Now set these options:

* **Name:** Django Server
* **Host:** 0.0.0.0
* **Port:** (use the http port specified in the docker-compose.yml file, e.g. 8080)`*` **Run browser** If checked, it will open the url after you click run. You should be able to access the running projecta on 0.0.0.0:61202 (the port that mapped to 8080)
* **Additional options:** ``--settings=jobsp.settings_server``
* **Run browser:** Optionally set this to your IP address (MacOS/Linux) or your specific IP address (Windows) followed by the port forward address for port 8080 specified in your ``docker-compose.yml`` file. For example: ``http://0.0.0.0:65202``.
* **Environment vars:** Leave as default unless you need to add something to the env
* **Python interpreter:** Ensure it is set you your remote interpreter (should be
  set to that by default)
* **Interpreter options:** Leave blank
* **Path mappings:** Here you need to indicate path equivalency between your host
  filesystem and the filesystem in the remote (docker) host. Click the ellipsis
  and add a run that points to your git checkout on your local host and the
  /home/web directory in the docker host. e.g.
  * **Local path:** <path to your git repo>/django_project
  * **Remote path:** /home/web/django_project
* click OK to save your run configuration

Now you can run the server using the green triangle next to the Django server
label in the run configurations pull down. Debug will also work and you will be
able to step through views etc as you work.


## Running Tests

sonlinux write stuff here....
