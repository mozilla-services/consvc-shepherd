import logging

from django.conf import settings
from django.core.files.storage import default_storage


def send_to_storage(content):
    if settings.DEBUG:
        logging.info(f"Sending to storage, name:{settings.GS_BUCKET_FILE_NAME}, content: {content}")
    else:
        current_file_name = f"{settings.GS_BUCKET_FILE_NAME}-current.json"
        # write content in -current file to another file
        if default_storage.exists(current_file_name):
            creation_date = default_storage.get_created_time(current_file_name)

            current_file = default_storage.open(current_file_name,"r")
            current_file_contents = current_file.read()
            previous_file_name =f"{settings.GS_BUCKET_FILE_NAME}-{creation_date}"

            previous_file = default_storage.open(previous_file_name, "w")
            previous_file.write(current_file_contents)
            previous_file.close()

        file = default_storage.open(current_file_name, "w")
        file.write(content)
        file.close()
