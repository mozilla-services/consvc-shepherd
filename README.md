# Contextual Services Shepherd

This is a tool to manage dynamic settings for Contextual Services projects like
Merino and Contile. The settings managed here can be changed at runtime,
reducing the need for deployments of the services that use it.

## Quick Start

To use consvc-shepherd, you'll need a Python 3.11 development environment and
Poetry installed. To achieve this, it is recommended you use a Python virtual environment.

venv is a viable option, but for ease you can use pyenv-virtualenv as a plugin for
pyenv and virtual environments. Using virtualenv creates a `.python-version` file  in the project
directory and if you add `eval "$(pyenv virtualenv-init -)"` to your  `./bashrc` or `./zshrc`,
the environment will automatically be activated. See the [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)
documentation for more information.

Ex:
```shell
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

You also need to ensure you have Postgres installed. You can select a distribution from
[https://www.postgresql.org/download/](https://www.postgresql.org/download/), use homebrew
or their EDB installer client.  Make sure to install version 14.7, or equivalent, and have
it running when developing for consvc-shepherd.

You'll want to make sure configuration files in the `.env` file match your database setup,
configuring the database name, user, host and password variables. See below for details.
You can configure the database using pgAdmin, cli or configuration files.

You'll need to specify some minimal configuration. Create a file `.env` and put the
following variables in it at least, if using the docker workflow. The simplest way is to
use `.env.example` and rename it to `env`:

```shell
$ mv .env.example .env

# Variables to set in file
DEBUG=true
SECRET_KEY=keyboard-mash
DB_NAME=postgres
DB_USER=postgres
DB_HOST=localhost
DB_PASS=
```

Then, set up your virtual environment:

```shell
# Prepare a virtual environment (customize this as you see fit).

# pyenv verison install
$ pyenv install 3.11

# pyenv virtualenv
$ pyenv virtualenv 3.11 shepherd # or whatever project name you like.
$ pyenv local shepherd

# venv
$ python -m venv .venv
$ source .venv/bin/activate
```
Install your dependencies:
```shell
$ poetry install
```

With your environment ready, you can set up the Django site:
```shell
# Set up Django
$ ./manage.py migrate
$ ./manage.py createsuperuser
```

After that is done, you can run the development server:
```shell
# Activate the virtualenv, if not already active:
# pyenv virtualenv 
$ pyenv local shepherd
# venv
$ source .venv/bin/activate

# Start the app:
$ ./manage.py runserver

# To run on alternate port if in use:
$ ./manage.py runserver localhost:8001
```

This will start a development server that reloads on changes to the files. You
can access the configuration part of the site at
`[http://localhost:8000/admin](http://localhost:8000/admin).`

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