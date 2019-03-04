import requests
from utils import cp
r = requests.get('https://currate.ru/api/?get=rates&pairs=USDUAH&key=73cc3bac382ccec5064975b32d4c71d7')
# cp(r.json()['data']['UAHRUB'])
cp(r.json())