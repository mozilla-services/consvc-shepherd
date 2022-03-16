import logging

from django.conf import settings
from django.core.files.storage import default_storage


def send_to_storage(content_name, content):
    if settings.DEBUG:
        logging.info(f"Sending to storage name:{content_name}, content: {content}")
    else:
        file = default_storage.open(content_name, "w")
        file.write(content)
        file.close()
