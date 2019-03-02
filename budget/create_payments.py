from budget.models import Payment
import random
import string

for p in range(100):
    N = 10
    desc = ''.join(random.choices(string.ascii_uppercase + string.digits, k=N))
    amount = random.uniform(0, 100)
    Payment.objects.create(description=desc, amount=amount)
