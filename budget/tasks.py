from transactions.gsheets import update_record
import logging

logger = logging.getLogger(__name__)
from huey.contrib.djhuey import task


@task(retries=2, retry_delay=10)
def huey_update_record(i):
    r = update_record(i)
    if r:
        logger.info('successfully update ghseet record')
    else:
        raise Exception('failed to update gsheet record')
    return r
