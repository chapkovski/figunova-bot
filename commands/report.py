from dateutil import parser
from datetime import datetime
import pytz
from budget.models import Payment
from django.db.models import CharField, Sum, Min, Max, Value as V
from django.db.models.functions import Concat
from telegram.ext import CommandHandler
import logging
from commands.utils import get_user
from telegram.ext import MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from .keyboards import month_report_keyboard

logger = logging.getLogger(__name__)

MONTH_SELECT = 1


def start_report(update, context):

    update.message.reply_text(f'Выберите месяц', reply_markup=month_report_keyboard())
    return MONTH_SELECT


def report_request(update, context):
    month = context.match.groupdict().get('month')
    year = context.match.groupdict().get('year')
    report = Payment.objects.report(month, year)
    return ConversationHandler.END


report_handler = CommandHandler("report", start_report, pass_args=True)

report_chat_handler = ConversationHandler(
    entry_points=[report_handler],
    states={
        MONTH_SELECT: [CallbackQueryHandler(report_request,
                                            pattern=r'^month_(?P<month>\d{2})_(?P<year>\d{4})$',
                                            pass_user_data=True)],
    },
    fallbacks=[
        # MessageHandler(Filters.text, unclear_data, pass_user_data=True)
    ],

)
