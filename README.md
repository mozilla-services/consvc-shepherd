# Contextual Services Shepherd

This is a tool to manage dynamic settings for Contextual Services projects like
Merino and Contile. The settings managed here can be changed at runtime,
reducing the need for deployments of the services that use it.

## Quick Start

To use consvc-shepherd, you'll need a Python 3.10 development environment.

You'll need to specify some minimal configuration. Create a file `.env` and put
in it at least, if using the docker workflow, you may want to use `.env.example` 
and rename it to `env`:

```shell
DEBUG=true
SECRET_KEY=keyboard-mash
```

With that ready, you can set up the Django site:

```shell
# Prepare a virtual environment (customize this as you see fit)
$ python -m venv .venv
$ source .venv/bin/activate

# Install bootstrap-dependencies
$ pip install -U pip pip-tools

# Install dependencies
$ pip-sync

# Set up Django
$ ./manage.py migrate
$ ./manage.py createsuperuser
```

After that is done, you can run the development server:

```shell
# Activate the virtualenv, if not already active
$ source .venv/bin/activate

# Start the app
$ ./manage.py runserver
```

This will start a development server that reloads on changes to the files. You
can access the configuration part of the site at
[localhost:8000/admin][http://localhost:8000/admin].

### Docker set up

Start with building and get it up with:
```
docker compose build
docker compose up
```
To create a user, shell into the container and run
``` 
./manage.py createsuperuser
```