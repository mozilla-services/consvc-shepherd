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
Use the existing `.env.example` and copy it to `.env`.
You'll want to make sure configuration files in the `.env` file match your database setup, configuring the database name, user, host,password and boostr JWT token variables.
It should appear as follows:

```shell
$ cp .env.example .env

# Variables to set in file
DEBUG=true
SECRET_KEY=keyboard-mash
DB_NAME=postgres
DB_USER=postgres
DB_HOST=db
DB_PASS=postgres
BOOSTR_JWT=""
```
To get the BOOSTR_JWT token run the following and paste the token into the .env file:

```shell
$ curl --location 'https://app.boostr.com/api/user_token' \
--header 'Content-Type: application/json' \
--data-raw '{
    "auth": {
        "email": "get-from-Ads-Engr-1password",
        "password": "get-from-Ads-Engr-1password"
    }
}'
```

5. Set up and enable your virtual environment:

```shell
# pyenv version install
$ pyenv install 3.11

# pyenv virtualenv
$ pyenv virtualenv 3.11 shepherd # or whatever project name you like.
$ pyenv local shepherd # enables virtual env when you enter directory.
```

6. Install your dependencies:

```shell
$ pip install poetry
$ poetry install
```

7. [Install Docker](https://docs.docker.com/engine/install/) if not already installed.

8. Build the Docker image and start the container:
```shell
docker compose up --build
```

The application will then be accessible at the following url: [http://0.0.0.0:7001/](http://0.0.0.0:7001/). The admin panel is available at [http://0.0.0.0:7001/admin](http://0.0.0.0:7001/admin)

9. Create database migrations and run migrations.
You may have to do this periodically as you modify or create models. Shell in as above and run the following commands:
``` shell
docker exec -it consvc-shepherd-app-1 sh # interactive mode
python manage.py makemigrations
python manage.py migrate
```
10. Import Boostr Deals and Products
``` shell
docker exec -it consvc-shepherd-app-1 sh # interactive mode you many not need this if you just completed step 9
python sync_boostr_data.py
```
