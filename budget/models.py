import pytz
import datetime
from lenin.quote_requester import get_new_quote
from exceptions import NoConnection, NoSuchCurrency
# Create your models here.

from django.db import models
from jsonfield import JSONField


class TimeStampModel(models.Model):
    class Meta:
        abstract = True
        ordering = ['-timestamp']
        get_latest_by = 'timestamp'

    timestamp = models.DateTimeField(auto_now_add=True)


class Category(models.Model):
    class Meta:
        verbose_name_plural = "Categories"

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=10000)
    emoji = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.name} ({self.description})'


class Payment(TimeStampModel):
    amount = models.FloatField()
    description = models.CharField(max_length=100000)
    creator = models.ForeignKey(to='Payer', related_name='payments', on_delete=models.CASCADE)
    category = models.ForeignKey(to='Category', related_name='payments', on_delete=models.CASCADE, null=True)
    update = models.CharField(max_length=1000, unique=True)

    def __str__(self):
        return f'{self.creator} заплатил {self.amount} за {self.description} числа: {self.timestamp}'


class Payer(models.Model):
    first_name = models.CharField(max_length=100000, null=True, blank=True)
    last_name = models.CharField(max_length=100000, null=True, blank=True)
    telegram_id = models.CharField(max_length=100000, unique=True, primary_key=True)
    show_cats = models.NullBooleanField(verbose_name='Show categories when the payment is registered')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_current_currency(self):
        curs = self.currencies.all()
        if curs.exists():
            return curs.latest().name
        else:
            # We assume that if there are no records, user still uses roubles
            return 'RUB'

    def get_rate(self):
        curs = self.currencies.all()
        if curs.exists():
            curcurs = curs.latest()
            if curcurs.name == 'RUB':
                return 1
            else:
                return CurrencyQuote.get_quote(curcurs.name)
        else:
            # We assume that if there are no records, user still uses roubles
            return 1


class Currency(TimeStampModel):
    class Meta:
        verbose_name_plural = "Currencies"

    payer = models.ForeignKey(to='Payer', related_name='currencies', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)


class CurrencyQuote(TimeStampModel):
    @classmethod
    def _get_new_quote(cls):
        quote = get_new_quote()
        if quote:
            return cls.objects.create(quote=quote)
        else:
            return False

    @classmethod
    def _get_or_update(cls):
        today_date = datetime.datetime.now().replace(tzinfo=pytz.UTC)
        quotes = cls.objects.all()
        if quotes.exists():
            if quotes.latest().timestamp.date() < today_date.date():
                new_quote = cls._get_new_quote()
                # If we can't retrieve new quotes for some reasons (website is down or whatever) - we take the
                # last existiting quote. Better than nothing.
                if new_quote:
                    return new_quote
                else:
                    return quotes.latest()
            else:
                return quotes.latest()
        else:
            # Again if no quotes exist BUT there is no connection or whatever, then we return false
            new_quote = cls._get_new_quote()
            if new_quote:
                return new_quote
            else:
                raise NoConnection

    @classmethod
    def get_quote(cls, curname):
        l = cls._get_or_update()
        valute = l.quote['Valute'].get(curname)
        if valute:
            value = valute['Value']
            nominal = valute['Nominal']
            return value / nominal
        else:
            raise NoSuchCurrency

    quote = JSONField()
