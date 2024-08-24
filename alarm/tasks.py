from celery import shared_task

from lecture_management_system.utils import log


@shared_task
def send_alerts_task():
    from .utils import send_alerts

    errors = send_alerts()
    if errors:
        log.error(f"Errors occurred: {errors}")
        raise Exception(f"Errors occurred: {errors}")
