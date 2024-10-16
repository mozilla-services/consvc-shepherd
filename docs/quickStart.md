# Quick Start Development Guide

Shepherd is a grab-bag of Ad Operations tools, and currently consists of
* `consvc_shepherd`: A full-stack Python Django app, as well as a json REST API
* `contile`: A Python Django app
* `ad-ops-dashboard`: A Node/Typescript React app, backed by the `consvc_shepherd` REST API

## Python setup

To use consvc-shepherd, you'll need a Python 3.11 development environment with Poetry installed and Docker.

It is recommended to use `pyenv` and the `pyenv-virtualenv` plugin for your virtual environment.
1. Install `pyenv` using the [latest documentation](https://github.com/pyenv/pyenv#installation) for your platform.
1. Follow the instructions to install the `pyenv-virtualenv` plugin.
See the [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) documentation.
1. Ensure you've added `pyenv` and `pyenv-virtualenv` to your `PATH`:

    Ex:
    ```shell
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
    ```

    To run consvc-shepherd, you'll need to specify some minimal configurations.
    Use the existing `.env.example` and copy it to `.env`.

    You'll want to make sure the environment variables in the `.env` file match your database setup, configuring the database name, user, host, and password.

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
    ```

1. Set up and enable your virtual environment:

    ```shell
    # pyenv version install
    $ pyenv install 3.11

    # pyenv virtualenv
    $ pyenv virtualenv 3.11 shepherd # or whatever project name you like.
    $ pyenv local shepherd # enables virtual env when you enter directory.
    ```

1. Install your dependencies:

    ```shell
    $ pip install poetry
    $ poetry install
    ```

1. [Install Docker](https://docs.docker.com/engine/install/), if not already installed.

1. Build the Docker image and start the container:
    ```shell
    docker compose up --build
    ```

    The application will then be accessible at the following url: [http://0.0.0.0:7001/](http://0.0.0.0:7001/). The admin panel is available at [http://0.0.0.0:7001/admin](http://0.0.0.0:7001/admin).

1. Create database migrations and run migrations.

    You may have to do this periodically as you modify or create models. Shell in as above and run the following commands:
    ```shell
    docker exec -it consvc-shepherd-app-1 bash # can also be run with `make debug`
    python manage.py makemigrations
    python manage.py migrate
    ```

1. Connect to the DB with `psql`.

    While the Django Admin interface at `/admin` shows all the data in our DB in a human readable way, it may sometimes be
    helpful to connect directly to the Shepherd DB while developing.

    **Note**: The values for the DB user and DB name come from the `.env` file.

    ```shell
    docker exec -it consvc-shepherd-db-1 psql -U postgres postgres
    ```

1. **(Optional)** Seed Shepherd DB with random test data. This is useful when testing schema changes without having to run our sync scripts to get real data.

    Shell into the `consvc-shepherd-app-1` container as mentioned above and run the following command:
    ```shell
    python manage.py seed
    ```

    The script will output a success message once the database has been seeded:
    ```shell
    Successfully seeded the database with random data
    ```

    Shell into `psql` and describe any of the DB tables (see example below), you should see that it contains some random data. Alternatively, you can look at the data by accessing the admin console at [http://0.0.0.0:7001/admin](http://0.0.0.0:7001/admin).
    ```shell
    SELECT * FROM consvc_shepherd_deliveredflight;
    ```

1. Import Boostr Deals and Products.

    If you're working with the AdOps dashboard, you may want to pull in Boostr Deals and Products.

    First, make sure you have the Boostr API credentials set in your `.env` file. You can find them in 1Password.

    ```shell
    BOOSTR_API_EMAIL=find-me-in-1password@mozilla.com
    BOOSTR_API_PASS=i-am-in-1password-too
    ```

    Then, run the script:

    ```shell
    docker exec -it consvc-shepherd-app-1 bash # can also be run with `make debug`
    python manage.py sync_boostr_data https://app.boostr.com/api
    ```

## Node/Typescript setup

To develop on the ad-ops-dashboard app, you'll need `node` and `npm` installed.

It is recommended to use a node version manager to allow for multiple `node`s on your system

1. Install a node version manager. [nvm](https://github.com/nvm-sh/nvm) is a great
  choice if you're developing on a macOS with a POSIX-compliant shell.

2. `cd ad-ops-dashboard`

3. Install the `node` version specified in `ad-ops-dashboard/.nvmrc`:

    ```shell
    $ nvm install
    ```

4. Install `ad-ops-dashboard` app's dependencies:

    ```shell
    $ npm install
    ```
5. Set up the `ad-ops-dashboard` environment:

    ```shell
    $ cp .env.example .env
    ```
6. Spin up the `ad-ops-dashboard` app and REST api together:

    ```shell
    $ cd ..
    $ docker-compose up --build
    ```

    (You can also run the `ad-ops-dashboard` without the API via `npm run dev` from `./ad-ops-dashboard`)

7. Visit the home page at http://0.0.0.0:5173/
