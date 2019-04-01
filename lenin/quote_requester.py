import requests
from requests.exceptions import ConnectionError
import logging


logger = logging.getLogger(__name__)

def get_new_quote():
    try:
        r = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
    except ConnectionError:
        logger.warning('No connection to get quotes')
        return False
    if r.status_code == 200:
        return r.json()
    else:
        logger.warning('Quote server returns a non-200 code (failure)')
        return False
