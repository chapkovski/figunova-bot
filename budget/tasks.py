from django.conf import settings
huey = settings.HUEY
from transactions.gsheets import update_record
import logging
logger = logging.getLogger(__name__)

@huey.task()
def huey_update_record(i):

    r = update_record(i)
    if r:
        logger.info('successfully update ghseet record')
    else:
        logger.warning('failed to update gsheet record')
    return r