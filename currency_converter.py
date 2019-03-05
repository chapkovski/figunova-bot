import requests
from utils import cp
# r = requests.get('https://currate.ru/api/?get=rates&pairs=USDUAH&key=73cc3bac382ccec5064975b32d4c71d7')
# a = r.json()['data']['USDUAH']
# cp(r.json())
#
# r = requests.get('https://currate.ru/api/?get=rates&pairs=RUBUSD&key=73cc3bac382ccec5064975b32d4c71d7')
# b= r.json()['data']['RUBUSD']
# cp(r.json())
# cp(1/(float(a)*float(b)))

r = requests.get('https://www.cbr-xml-daily.ru/daily_json.js')
cp(r.json()['Valute']['UAH']['Value'])
cp(r.json()['Valute']['UAH']['Nominal'])
cp(r.json()['Valute']['USD']['Value'])
cp(r.json()['Valute']['TRY']['Value'])
cp(r.json()['Valute']['TRY']['Nominal'])