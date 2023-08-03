# Quick Start Development Guide

To use consvc-shepherd, you'll need a Python 3.11 development environment with Poetry installed and Docker.

It is recommended to use `pyenv` and the `pyenv-virtualenv` plugin your virtual environments.
1. Install `pyenv` using the [latest documentation](https://github.com/pyenv/pyenv#installation) for your platform.
2. Follow the instructions to install the `pyenv-virtualenv` plugin.
See the [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) documentation.
3. Ensure you've added `pyenv` and `pyenv-virtualenv` to your PATH.

Ex:
```shell
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
```

4. To run consvc-shepherd, you'll need to specify some minimal configurations.
Use the existing `.env.example` and rename it to `env`.
You'll want to make sure configuration files in the `.env` file match your database setup, configuring the database name, user, host and password variables.
It should appear as follows:

```shell
$ mv .env.example .env

# Variables to set in file
DEBUG=true
SECRET_KEY=keyboard-mash
DB_NAME=postgres
DB_USER=postgres
DB_HOST=db
DB_PASS=postgres
```

5. Set up and enable your virtual environment:

```shell
# pyenv version install
$ pyenv install 3.11

# pyenv virtualenv
$ pyenv virtualenv 3.11 shepherd # or whatever project name you like.
$ pyenv local shepherd # enables virtual env when you enter directory. 

# Install dependencies
$ pip install poetry
$ poetry install
```

6. Install your dependencies:
```shell
$ poetry install
```

7. [Install Docker](https://docs.docker.com/engine/install/) if not already installed.

8. Build the Docker image and start the container:
```shell
docker compose build
docker compose up
```

The application will then be accessible at the following url: [http://0.0.0.0:7001/](http://0.0.0.0:7001/). The admin panel is available at [http://0.0.0.0:7001/admin](http://0.0.0.0:7001/admin)

9. Create a super user by shelling into the container. Run the following:
``` shell
docker ps # capture container id for consvc-shepherd
docker exec -it <CONTAINER ID> sh # interactive mode
./manage.py createsuperuser # follow directions to create superuser
```