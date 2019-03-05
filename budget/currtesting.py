from budget.models import CurrencyQuote
from utils import cp
from budget.models import Payment, Payer
import datetime
import random
import string
a = 0
for p in Payment.objects.all():
    a+=p.amount
    cp(p.creator, p.timestamp, p.amount)
cp(a)
# from django.db.models import Sum, Avg, Min, Max
# # Payment.objects.all().delete()
# # todayDate = datetime.datetime.now().replace(day=1)
# # cp(todayDate)
# N = 10
# payer = Payer.objects.all().first()
# for i in range(1,5):
#     todayDate = datetime.datetime.now().replace(day=i)
#     desc = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))
#     p1 = payer.payments.create(amount=random.randint(0,1000), description='asdf', timestamp=todayDate, update=desc)
#     p1.save()
#     p1.timestamp = todayDate
#     p1.save()
# desc = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))
# p2 = payer.payments.create(amount=456, description='asdf',  update=desc)

# for p in Payment.objects.all():
#     print(p.timestamp, p.amount)
# p = Payment.objects.all().dates('timestamp', 'day').aggregate(Min('timestamp'), Max('timestamp'))
# print((p['timestamp__max']-p['timestamp__min']).days)