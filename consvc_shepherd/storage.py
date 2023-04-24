import logging

from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone


def send_to_storage(content, alt_file_name:str ="") -> None:
    file_name: str = alt_file_name if alt_file_name else settings.GS_BUCKET_FILE_NAME

    if settings.DEBUG:
        logging.info(
            f"Sending to storage, name:{file_name}, content: {content}"
        )
    else:
        current_time_string = timezone.now().strftime("%Y%m%d%H%M%S")
        latest_file_name =    f"{file_name}_latest.json"  
        date_file_name = f"{file_name}_{current_time_string}.json"

        date_file = default_storage.open(date_file_name, "w")
        date_file.write(content)
        date_file.close()

        latest_file = default_storage.open(latest_file_name, "w")
        latest_file.write(content)
        latest_file.close()
