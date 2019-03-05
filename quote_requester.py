import requests
from utils import cp
from requests.exceptions import ConnectionError
# r = requests.get('https://currate.ru/api/?get=rates&pairs=USDUAH&key=73cc3bac382ccec5064975b32d4c71d7')
# a = r.json()['data']['USDUAH']
# cp(r.json())
#
# r = requests.get('https://currate.ru/api/?get=rates&pairs=RUBUSD&key=73cc3bac382ccec5064975b32d4c71d7')
# b= r.json()['data']['RUBUSD']
# cp(r.json())
# cp(1/(float(a)*float(b)))
def get_new_quote():
    try:
        r = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
    except ConnectionError:
        return False
    if r.status_code == 200:
        return r.json()
    else:
        return False
