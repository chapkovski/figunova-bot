from enum import Enum, unique


@unique
class CurrencyChatChoices(Enum):
    choosing_currency = 0
    pop_currency_choice = 1
    custom_currency_choice = 2
    input = 3


@unique
class ChartChoices(Enum):
    choosing_user = 0


class Color:
    Red = "FF0000"
    Green = "00FF00"
    Blue = "0000FF"
    Black = "000000"
    White = "FFFFFF"


pop_currencies = ['RUB', 'USD', 'EUR', 'UAH']
regex_pop_currencies = '|'.join(pop_currencies)
