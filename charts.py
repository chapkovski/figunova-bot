from transliterate import translit
from budget.models import Payment, Payer
from utils import cp
from django.db.models.functions import TruncDay
from django.db.models import Sum
from constants import Color
from datetime import datetime, timedelta
from urllib.parse import urlencode
import numpy as np


def trans_ru(text):
    """Translit text to  latin to guarantee that it will correctly rendered"""
    return translit(text, 'ru', reversed=True)


key_correspondence = {'chart_type': 'cht',
                      'size': 'chs',
                      'axes': 'chxt',
                      'axis_labels': 'chxl',
                      'data': 'chd',
                      'title': 'chtt',
                      'line_style': 'chls',
                      'line_color': 'chco',
                      'legend': 'chdl'
                      }


class Chart:
    entry_point = 'https://image-charts.com/chart'
    chart_type = 'lc'
    size = '700x300'
    max_days = 30

    def __init__(self):
        self.axes = 'x,y'

    def ltoc(self, l: list, sep=',') -> str:
        """Convert lists to  comma separated strings"""
        return f'{sep}'.join(str(e) for e in l)

    def piper(self, l: list) -> list:
        """chain list of lists by pipe symbol, convert inner lists to comma separated strings"""
        return self.ltoc([self.ltoc(i) for i in l], sep='|')

    def build_x_axis(self, xaxis_data):
        return f'0:|{self.ltoc(xaxis_data, sep="|")}'

    def get_lfit(self, data):
        x = range(len(data))
        y = data
        a, b = np.polyfit(x, y, deg=1)
        predicted = [a * i + b for i in x]
        return predicted

    def build_series(self, data):
        l = [data, self.get_lfit(data)]
        return f'a:{self.piper(l)}'

    def get_line_style(self):
        first_line = [3, 6, 3]
        second_line = [5]
        lines = [first_line, second_line]
        return self.piper(lines)

    def get_legend(self):
        legend_names = ['Траты в день', 'Тренд']
        legend_names = [trans_ru(i) for i in legend_names]
        return self.ltoc(legend_names, sep='|')

    def get_line_color(self):
        return f'{Color.Blue}22,{Color.Red}'

    def get_context(self):
        axis_labels, data, = self.get_user_payments()
        self.axis_labels = self.build_x_axis(axis_labels)
        self.data = self.build_series(data)
        self.legend = self.get_legend()
        self.line_style = self.get_line_style()
        self.line_color = self.get_line_color()
        context = {}
        for k, v in key_correspondence.items():
            if hasattr(self, k):
                context[v] = getattr(self, k)
        return context

    def get_url(self):
        """convert object's attributes to dict and convert them via urlunparse"""
        return f'{self.entry_point}?{urlencode(self.get_context())}'

    def get_user_payments(self):
        """Builds a universal query based on filter param (ft) from payments.
        Returns list of items (day, sum_per_day) for a specific user.

        depth defines how many days back we will plot (30 by default).
        """
        depth = datetime.today() - timedelta(days=self.max_days)
        ft = {'timestamp__date__gte': depth,
              'creator': self.payer}
        payments = Payment.objects.filter(**ft).order_by(). \
            annotate(day=TruncDay('timestamp')). \
            values('day'). \
            annotate(sumamount=Sum('amount')).values('sumamount', 'day')
        days = [trans_ru(i['day'].strftime('%d-%b-%y')) for i in payments]
        amounts = [round(i['sumamount'], 0) for i in payments]
        return days, amounts


class IndividualChart(Chart):
    """Build a chart with  average spending per day for individual user."""
    def __init__(self, payer_id):
        self.payer_id = payer_id
        self.payer = Payer.objects.get(telegram_id=payer_id)
        self.title = trans_ru(str(self.payer))
        super().__init__()


class OverallChart(Chart):
    """Build a series of average spending per day for all registered users"""


def charts_builder(update, context):
    chat_id = update.effective_message.chat_id

    formatted_payments = ','.join(map(str, payments))

    template = f'{head}'
    url = f"""cht=lc&chs=700x300&chd=a:12,3,4,5,6|1,3,5,2,3,5|1,2,4,5,3&chdl=Ivanova|Filka|Gulin&chls=3|3|3&chtt=Гулин"""

    # update.message.reply_text("https://chart.googleapis.com/chart?cht=p3&chd=t:60,40&chs=800x300&chl=Yes|No")


# c = Chart('647209696')
# cp(c.get_user_payments())
