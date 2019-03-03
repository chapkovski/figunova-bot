print('hello!')
from access_gsheet import gsheet_register_payment
from django.conf import settings
from utils import cp
import django
from dateutil import parser
from django.db.models.functions import Concat
from django.db.models import CharField, Value as V

import pytz

django.setup()
from budget.models import Payment, Payer
import datetime
from django.db.models import Sum, Avg

# !/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.
#
# THIS EXAMPLE HAS BEEN UPDATED TO WORK WITH THE BETA VERSION 12 OF PYTHON-TELEGRAM-BOT.
# If you're still using version 11.1.0, please see the examples at
# https://github.com/python-telegram-bot/python-telegram-bot/tree/v11.1.0/examples

"""
Bot that registers the payments.
"""

import logging

import telegram
from emoji import emojize

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, StringRegexHandler
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
# todo: move to env. vars
TOKEN = '690401493:AAHuK1MUdQLCwMiSuhkZbXfoJ2YDvl6tgrc'
# todo: get rid
REQUEST_KWARGS = {
    'proxy_url': 'socks5://phobos.public.opennetwork.cc:1090',
    # Optional, if you need authentication:
    'urllib3_proxy_kwargs': {
        'username': '772114',
        'password': 'LHNHr5FX',
    }
}
"""Start the bot."""

updater = Updater(TOKEN,
                  # request_kwargs=REQUEST_KWARGS,
                  use_context=True)
dp = updater.dispatcher
bot = updater.bot
# this is the regex to catch payments
payment_regex = r'(?P<amount>[0-9]+([,.][0-9]*)?) (?P<rest>.+)'

help_message = '''
    Привет! Я - бот, который регистирует все наши траты. \n
    Если тебе надо ввести новую трату просто введи сумму а потом ее описание. \n
    Если хочется посмотреть отчет о тратах и среднюю сумму которую каждый из нас тратит в день набери 
    <code>/report</code>. По умолчанию отчет будет с первого числа этого месяца. \n
    Если тебе надо вывести отчет, начиная с другой даты, набери <code>/report 01.01.2018</code> - получишь отчет с 1 
    января 2018 года (или с любой другой даты :) ).
    \n Если  хочешь получить справку по командам (я буду добавлять новые...), то набери <code>/help</code>
    '''
# TODO START
# TODO alert when something is deleted
# if call.message:
#     if call.data == "test":
#         bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Пыщь")
#         bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="Пыщь!")
# TODO:
""" 
When somebody sends the request \delete we get him 5 last messages and inline keyboard to choose
which one to delete.
When he clicks on the button, the message id of callback data is passed back and the item is deleted.
The answer_callback_query reposnds a notification.
Previous message (with list of 5 last items) is deleted(??)
 
  """


def keyboard(items):
    """ Return keyboard with buttons to delete one item."""
    if not items.exists():
        return None
    delete_buttons_row = []
    for i, j in enumerate(items):
        delete_buttons_row .append(InlineKeyboardButton(f'{i + 1}', callback_data=j.update))
    cancel_row = [InlineKeyboardButton('Отмена', callback_data='cancel')]
    return InlineKeyboardMarkup( [delete_buttons_row, cancel_row])


def delete(update, context):
    n = 5
    user_id = update.message.from_user.id
    try:
        user = Payer.objects.get(telegram_id=user_id)
    except Payer.DoesNotExist:
        update.message.reply_text(f'Не могу найти никаких записей о тебе, чувак...')
        return
    last_n = Payment.objects.filter(creator=user)[:n]
    kb = keyboard(last_n)
    if last_n.exists():
        message = f"""
         <b>Выбери что удалить:</b>    
         """
        for i, p in enumerate(last_n):
            message += f"""
             {i + 1}. ({p.timestamp.strftime('%d-%m-%y')}) {p.description}: {p.amount}
            """
        update.message.reply_html(text=message, reply_markup=kb, )
    else:
        update.message.reply_text(f'Чет не могу найти последних трат. Спроси у фильки что за хуйня')
    if update.callback_query:
        update.callback_query.answer()


# TODO END


# todo: N largest (5 by default) of current user since a specific date
def largest(update, context):
    try:
        how_many = int(context.args[0])
    except (IndexError, ValueError):
        how_many = 5
    try:
        raw_date = context.args[1]

    except IndexError:
        todayDate = datetime.datetime.now()
        raw_date = str(todayDate.replace(day=1))
    try:
        date = parser.parse(raw_date)
    except ValueError:
        update.message.reply_text(f'Чет какая-то поебота вместо даты, попробуй еще раз...')
        return
    user_id = update.message.from_user.id
    try:
        user = Payer.objects.get(telegram_id=user_id)
    except Payer.DoesNotExist:
        update.message.reply_text(f'Не могу найти никаких записей о тебе, чувак...')
        return
    date = date.replace(tzinfo=pytz.UTC)
    payments = Payment.objects.filter(creator=user, timestamp__gte=date).order_by('-amount')[:how_many]
    if payments.exists():
        message = f"""
         <b>Top-{how_many} трат с {date.strftime('%d-%m-%y')}:</b> \n    
         """
        for i, p in enumerate(payments):
            message += f"""
             {i + 1}. ({p.timestamp.strftime('%d-%m-%y')}) {p.description}: {p.amount}
            """
        update.message.reply_html(text=message)
    else:
        update.message.reply_text(f'Никаких трат в этом периоде, везуха!')


def report(update, context):
    if context.args:
        try:
            date = parser.parse(context.args[0])
        except ValueError:
            update.message.reply_text(f'Не могу распознать дату, попробуйте еще раз...')
            return
    else:
        todayDate = datetime.datetime.now()
        date = todayDate.replace(day=1)
    date = date.replace(tzinfo=pytz.UTC)
    payments = Payment.objects.annotate(
        screen_name=Concat('creator__first_name', V(' '), 'creator__last_name',
                           output_field=CharField()), ).order_by().filter(
        timestamp__gte=date).values('screen_name').annotate(total_sum=Sum('amount'), avg_sum=Avg('amount'))
    if payments.exists():
        message = f"""
         <b>Траты начиная с {date.strftime('%d-%m-%y')}:</b> \n    
         """
        for p in payments:
            message += f"""
            <i>{p['screen_name']}</i>: Всего: <b>{p['total_sum']}</b>. В среднем за день: {p['avg_sum']} \n
            """
        update.message.reply_html(text=message)
    else:
        update.message.reply_text(f'Нет трат за этот период!')


def start(update, context):
    """Send a message when the command /start is issued."""

    update.message.reply_html(help_message)


def register_payment(update, context):
    date = update.effective_message.date
    update_id = update.update_id
    user_id = update.message.from_user.id
    fname = update.message.from_user.first_name
    lname = update.message.from_user.last_name
    user_info = {'first_name': fname, 'last_name': lname}
    user, _ = Payer.objects.get_or_create(telegram_id=user_id, defaults=user_info)
    """Connect to DB and register new payment there."""
    #
    raw_amount = context.match.groupdict().get('amount')
    val = float(raw_amount)
    rest = context.match.groupdict().get('rest')
    Payment.objects.create(amount=val,
                           description=rest,
                           creator=user,
                           update=update_id
                           )
    gsheet_register_payment(date=date, user_id=user_id, user_name=f'{fname} {lname}', val=val, rest=rest)
    success = emojize(':thumbsup:', use_aliases=True)
    update.message.reply_text(success, quote=False)


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_html(help_message)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def send_message(chat_id, text):
    users = [p for p in get_users() if p != str(chat_id)]
    if users:
        for u in users:
            bot.sendMessage(chat_id=u, text=text, )


def process_payment(update, context):
    register_payment(update, context)


def main():
    start_handler = CommandHandler("start", start)
    help_handler = CommandHandler("help", help)
    delete_handler = CommandHandler("delete", delete)
    report_handler = CommandHandler("report", report, pass_args=True)
    # we try to grasp all messages starting with digits here to process them as new records
    largest_handler = CommandHandler("largest", largest, pass_args=True)
    payment_handler = MessageHandler(Filters.regex(payment_regex), process_payment, pass_user_data=True)
    handlers = [start_handler, help_handler, delete_handler, largest_handler, report_handler, payment_handler]
    for handler in handlers:
        dp.add_handler(handler)

    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
