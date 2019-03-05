from budget.models import  CurrencyQuote
from utils import cp
cp(CurrencyQuote.get_quote('USD'))