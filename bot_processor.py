print('hello!')
from access_gsheet import write_val, get_users, register_user

# !/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.
#
# THIS EXAMPLE HAS BEEN UPDATED TO WORK WITH THE BETA VERSION 12 OF PYTHON-TELEGRAM-BOT.
# If you're still using version 11.1.0, please see the examples at
# https://github.com/python-telegram-bot/python-telegram-bot/tree/v11.1.0/examples

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
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

updater = Updater(TOKEN, request_kwargs=REQUEST_KWARGS, use_context=True)
dp = updater.dispatcher
bot = updater.bot
# this is the regex to catch payments
payment_regex = r'(?P<amount>[0-9]+([,.][0-9]*)?) (?P<rest>.+)'


def start(update, context):
    fname = update.message.chat.first_name
    lname = update.message.chat.last_name
    register_user(update.effective_message.chat_id, fname, lname)
    """Send a message when the command /start is issued."""
    update.message.reply_text(f'Привет {fname} {lname}! Итак, займемся твоими финансами...')


def register_payment(update, context):

    # todo
    print(update, """KKSKSKSKSKSKS""")
    raw_amount = context.match.groupdict().get('amount')
    val = float(raw_amount)
    rest =  context.match.groupdict().get('rest')
    fname = update.message.chat.first_name
    lname = update.message.chat.last_name
    write_val(date=update.message.date,
              name=f'{fname} {lname}',
              val=val,
              rest=rest)


def callback_eval(update, context):
    print(f'UPDATE:: {update}')
    print(f'CONTEXT:: {context}')
    query_data = update.callback_query.data
    if query_data == "payment_confirmed":
        pass
        # register_payment(update, context)

    elif query_data == "payment_cancelled":
        print('PAYMENT CANCELLED!!! ')
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')



def echo(update, context):
    group_chat_id = update.effective_message.chat_id
    sender_id = update.effective_user.id

    bot.send_message(chat_id=sender_id, text=f'personal message to: {sender_id}')
    bot.send_message(chat_id=group_chat_id, text=f'universal message to: {group_chat_id}')

    bot.send_message(chat_id=group_chat_id, text=emojize("yummy :cake:", use_aliases=True))
    custom_keyboard = [[emojize(":tongue:", use_aliases=True), emojize(":boy:", use_aliases=True)], ]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)

    bot.send_message(chat_id=group_chat_id,
                     text="Custom Keyboard Test",
                     reply_markup=reply_markup)






def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def send_message(chat_id, text):
    users = [p for p in get_users() if p != str(chat_id)]
    if users:
        for u in users:
            bot.sendMessage(chat_id=u, text=text, )



def process_payment(update, context):
    yes_button = InlineKeyboardButton(text="Yes \U0001F1E9\U0001F1EA", callback_data="payment_confirmed")
    no_button = InlineKeyboardButton(text="No \U0001F1FA\U0001F1F8", callback_data="payment_cancelled")
    # todo: emoji inline keyboard
    # custom_keyboard = [[emojize(":tongue:", use_aliases=True), emojize(":boy:", use_aliases=True)], ]
    yes_no_keyboard = InlineKeyboardMarkup([[yes_button, no_button], ])
    bot.sendMessage(chat_id=update.message.chat_id, text='Do you confirm the payment?',
                        reply_markup=yes_no_keyboard, message_id=update.message.message_id, matches=context.match)


def main():
    start_handler =  CommandHandler("start", start)
    help_handler = CommandHandler("help", help)
    # we try to grasp all messages starting with digits here to process them as new records
    payment_handler = MessageHandler(Filters.regex(payment_regex), process_payment)
    callback_handler = CallbackQueryHandler(callback_eval)
    handlers = [start_handler,help_handler, payment_handler, callback_handler]
    for handler in handlers:
        dp.add_handler(handler)


    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
