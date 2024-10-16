#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
from argparse import OPTIONAL
import os
import sys
import logging
import environ

from pathlib import Path


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "consvc_shepherd.settings")
    env = environ.Env(APP_ENV=(str, OPTIONAL))
    BASE_DIR = Path(__file__).resolve().parent.parent
    environ.Env.read_env(BASE_DIR / ".env")
    
    # For local dev, human readable timestamps are added to help with debugging.
    if env("APP_ENV") == "dev":
        logging.basicConfig(format="%(asctime)s.%(msecs)03d", level=logging.INFO, datefmt="%Y-%m-%d,%H:%M:%S")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
