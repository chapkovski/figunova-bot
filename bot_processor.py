print('hello!')
from access_gsheet import gsheet_register_payment, delete_gsheet_record
from utils import cp
import django
from dateutil import parser
from django.db.models.functions import Concat
from django.db.models import CharField, Value as V
from telegram import (ChatAction, ReplyKeyboardMarkup, ForceReply, ReplyKeyboardRemove)
from os import environ
import pytz
from functools import wraps
import datetime
from django.db.models import Sum, Avg, Min, Max
from constants import CurrencyChatChoices, regex_pop_currencies, pop_currencies

django.setup()
from budget.models import Payment, Payer, Currency, CurrencyQuote
from budget.exceptions import NoSuchCurrency

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

from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler)
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TOKEN = environ.get('TELEGRAM_API')
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
thousand_part = 'тыщ.?|тысяч.?|т|000'
# We filter out thousands in letters using negative look-ahead and lookbehind.
payment_regex = r'(?P<amount>[0-9]+([,.][0-9]*)?) (?P<rest>.+)'
# thousand_payment_regex = fr'^(?P<amount>[0-9]+([,.][0-9]*)?)\s?(?P<thousand>{thousand_part}) (?P<rest>.+)$'
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


def get_user(from_user):
    user_id = from_user.id
    fname = from_user.first_name
    lname = from_user.last_name
    user_info = {'first_name': fname, 'last_name': lname}
    user, _ = Payer.objects.get_or_create(telegram_id=user_id, defaults=user_info)
    return user


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context, *args, **kwargs)

    return command_func


def keyboard(items):
    """ Return keyboard with buttons to delete one item."""
    if not items.exists():
        return None
    delete_buttons_row = []
    for i, j in enumerate(items):
        delete_buttons_row.append(InlineKeyboardButton(f'{i + 1}', callback_data=j.update))
    cancel_row = [InlineKeyboardButton('Отмена', callback_data='cancel')]
    return InlineKeyboardMarkup([delete_buttons_row, cancel_row])


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
         <b>Твои top-{how_many} трат с {date.strftime('%d-%m-%y')}:</b>\n"""
        for i, p in enumerate(payments):
            message += f"""{i + 1}. ({p.timestamp.strftime('%d-%m-%y')}) {p.description}: {p.amount}\n"""
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
        date = todayDate.replace(day=1, hour=0, minute=0)
    date = date.replace(tzinfo=pytz.UTC)
    payments = Payment.objects.order_by().filter(timestamp__gte=date)
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


def start(update, context):
    """Send a message when the command /start is issued."""

    update.message.reply_html(help_message)


@send_typing_action
def register_payment(update, context):
    cp(update)
    date = update.effective_message.date
    update_id = update.update_id
    user = get_user(update.message.from_user)
    rate = user.get_rate()
    currency_name = user.get_current_currency()
    """Connect to DB and register new payment there."""
    #
    raw_amount = context.match.groupdict().get('amount')
    thousand = context.match.groupdict().get('thousand')
    t_corrector = 1000 if thousand else 1
    val = round(float(raw_amount) * t_corrector * rate, 2)

    rest = context.match.groupdict().get('rest')
    Payment.objects.create(amount=val,
                           description=rest,
                           creator=user,
                           update=update_id
                           )
    gsheet_register_payment(date=date,
                            user_id=user.telegram_id,
                            user_name=f'{user.first_name} {user.last_name}',
                            val=val,
                            rest=rest,
                            update_id=update_id)
    foreign_val = f'{raw_amount} {currency_name}; ' if currency_name != 'RUB' else ''
    success = emojize(f':white_check_mark: ({foreign_val}{val} рублей)', use_aliases=True)
    update.message.reply_text(success, quote=False)


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_html(help_message)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def cancel(update, context):
    user_data = context.user_data
    ReplyKeyboardRemove()
    return ConversationHandler.END


def receive_delete_msg(update, context):
    # cp(context.user_data)
    if update.callback_query.data == 'cancel':
        cp('отмена')
    else:
        try:
            update_id = update.callback_query.data
            Payment.objects.filter(update=update_id).delete()
            delete_gsheet_record(update_id)
        except Payment.DoesNotExist:
            update.message.reply_html('что-то пошло не так. Спросите у фильки')
    update.callback_query.answer(show_alert=False, text="Пыщь!")
    bot.delete_message(chat_id=update.callback_query.message.chat.id,
                       message_id=update.callback_query.message.message_id)
    # bot.answer_callback_query(callback_query_id=call.id, show_alert=False, text="Пыщь!")


def currency_start(update, context):
    reply_keyboard = [pop_currencies,
                      ['Другая валюта'],
                      ['Отмена']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(
        "Выбери валюту в которой ты хочешь вести учет",
        reply_markup=markup)

    return CurrencyChatChoices.choosing_currency


def custom_currency_choice(update, context):
    update.message.reply_text("Введите название валюты (три буквы типа USD, EUR. Если что - спросите у Фильки.",
                              reply_markup=ForceReply())
    return CurrencyChatChoices.input


def check_register_currency(update, context):
    currency_name = update.message.text.upper()
    if currency_name != 'RUB':
        try:
            quote = CurrencyQuote.get_quote(currency_name)
        except NoSuchCurrency:
            update.message.reply_text("Не могу найти название валюты. Попробуйте RUB или спросите у Фильки",
                                      reply_markup=ForceReply())
            return CurrencyChatChoices.input
    user = get_user(update.message.from_user)
    user.currencies.create(name=currency_name)
    if currency_name != 'RUB':
        update.message.reply_text(f"Теперь все твои траты будут считаться в {currency_name} по курсу {quote} рублей")
    else:
        update.message.reply_text(f"Считаем отныне все в старых добрых рублях")
    return currency_done(update, context)


def currency_done(update, context):
    user_data = context.user_data
    user_data.clear()
    update.message.reply_text("\U0001F44D", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    start_handler = CommandHandler("start", start)
    help_handler = CommandHandler("help", help)
    delete_handler = CommandHandler("delete", delete)
    report_handler = CommandHandler("report", report, pass_args=True)
    # we try to grasp all messages starting with digits here to process them as new records
    largest_handler = CommandHandler("largest", largest, pass_args=True)
    payment_handler = MessageHandler(Filters.regex(payment_regex),
                                     register_payment, pass_user_data=True)
    callback_delete_handler = CallbackQueryHandler(receive_delete_msg, pass_user_data=True)
    ########### BLOCK: CONVERSATION ABOUT CURRENCY ##############################################################
    popular_currency_handler = MessageHandler(Filters.regex(f'^({regex_pop_currencies})$'),
                                              check_register_currency,
                                              pass_user_data=True)
    custom_choice_handler = MessageHandler(Filters.regex(f'^Другая валюта$'),
                                           custom_currency_choice,
                                           pass_user_data=True)
    currency_input_handler = MessageHandler(Filters.text,
                                            check_register_currency,
                                            pass_user_data=True)

    done_handler = MessageHandler(Filters.regex('^Отмена$'),
                                  currency_done,
                                  pass_user_data=True)
    currency_chat_handler = ConversationHandler(
        entry_points=[CommandHandler('currency', currency_start)],
        states={
            CurrencyChatChoices.choosing_currency: [popular_currency_handler,
                                                    custom_choice_handler,
                                                    ],
            CurrencyChatChoices.input: [currency_input_handler],

        },
        fallbacks=[done_handler]
    )
    ############ END OF: CONVERSATION ABOUT CURRENCY #############################################################

    handlers = [start_handler, help_handler, delete_handler, callback_delete_handler,
                largest_handler, report_handler, currency_chat_handler, payment_handler]
    for handler in handlers:
        dp.add_handler(handler)

    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
