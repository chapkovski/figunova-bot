from dateutil import parser
from datetime import datetime
import pytz
from budget.models import Payment
from django.db.models import CharField, Sum, Min, Max, Value as V
from django.db.models.functions import Concat
from telegram.ext import CommandHandler
import logging
from commands.utils import get_user

logger = logging.getLogger(__name__)

def report(update, context):
    user = get_user(update.message.from_user)

    if context.args:
        try:
            date = parser.parse(context.args[0])
        except ValueError:
            update.message.reply_text(f'Не могу распознать дату, попробуйте еще раз...')
            return
    else:
        todayDate = datetime.now()
        date = todayDate.replace(day=1, hour=0, minute=0)
    date = date.replace(tzinfo=pytz.UTC)
    payments = Payment.objects.order_by().filter(timestamp__gte=date)
    logger.info(f'User with id {user.telegram_id} asked for a report starting at {date}')
    if payments.exists():
        minmaxpayments = payments.aggregate(Min('timestamp'), Max('timestamp'))
        numdays = (minmaxpayments['timestamp__max'] - minmaxpayments['timestamp__min']).days + 1
        payments = payments.annotate(
            screen_name=Concat('creator__first_name', V(' '), 'creator__last_name',
                               output_field=CharField()), ). \
            values('screen_name').annotate(total_sum=Sum('amount'), avg_sum=(Sum('amount') / numdays))

        message = f"""<b>Траты начиная с {date.strftime('%d-%m-%y')}:</b>\n"""
        for p in payments:
            message += f"""<i>{p['screen_name']}</i>: Всего: <b>{round(p['total_sum'],
                                                                       0)}</b>. В среднем за день: {round(p['avg_sum'],
                                                                                                          0)}\n"""
        update.message.reply_html(text=message)
    else:
        update.message.reply_text(f'Нет трат за этот период!')
    logger.info(f'Successfully delivered report to user with id {user.telegram_id} with info starting at {date}')


report_handler = CommandHandler("report", report, pass_args=True)
