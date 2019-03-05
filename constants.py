from enum import Enum

CurrencyChatChoices = Enum('CurrencyChatChoice', 'CHOOSING_CURRENCY POP_CURRENCY_CHOICE CUSTOM_CURRENCY_CHOICE')
pop_currencies = ['USD', 'EUR', 'CFH', 'UAH']
regex_pop_currencies = '|'.join(pop_currencies)
