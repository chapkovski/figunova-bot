from enum import Enum, unique


@unique
class CurrencyChatChoices(Enum):
    choosing_currency = 0
    pop_currency_choice = 1
    custom_currency_choice = 2
    input = 3


pop_currencies = ['RUB', 'USD', 'EUR', 'UAH']
regex_pop_currencies = '|'.join(pop_currencies)
