from charts import  IndividualChartPerDay as I
from budget.models import Payer
p = Payer.objects.get()
x = p.telegram_id
i=I(x)
print(i.get_url())