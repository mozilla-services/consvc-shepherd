# Contextual Services Shepherd

This is a tool to manage dynamic settings for Contextual Services projects like
Merino and Contile. The settings managed here can be changed at runtime,
reducing the need for deployments of the services that use it.

To use consvc-shepherd, you'll need a Python development environment, and
[Poetry][]. With that ready, you can set up the Django site:

```shell
$ poetry shell
$ poetry install
$ ./manage.py migrate
$ ./manage.py createsuperuser
```

and run the admin site:

```shell
$ ./manage.py runserver
```

This will start a development server that reloads on changes to the files. You
can access the editing part of the site at
[localhost:8000/admin][http://localhost:8000/admin].

[poetry]: https://python-poetry.org/
