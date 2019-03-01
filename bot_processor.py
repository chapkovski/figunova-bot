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

from telegram import ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters,StringRegexHandler
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
import re

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TOKEN = '690401493:AAHuK1MUdQLCwMiSuhkZbXfoJ2YDvl6tgrc'

REQUEST_KWARGS = {
    'proxy_url': 'socks5://phobos.public.opennetwork.cc:1090',
    # Optional, if you need authentication:
    'urllib3_proxy_kwargs': {
        'username': '772114',
        'password': 'LHNHr5FX',
    }
}
updater = Updater(TOKEN, request_kwargs=REQUEST_KWARGS, use_context=True)
dp = updater.dispatcher
bot = updater.bot
get_users()
payment_regex = r'(?P<amount>[0-9]+([,.][0-9]*)?) (?P<rest>.+)'

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    fname = update.message.chat.first_name
    lname = update.message.chat.last_name
    register_user(update.effective_message.chat_id, fname, lname)
    """Send a message when the command /start is issued."""
    update.message.reply_text(f'Привет {fname} {lname}! Итак, займемся твоими финансами...')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def smth(update, context):
    print(update.message.text, 'TEST!!!!')


def echo(update, context):
    print('AAAAUUUU', update)
    group_chat_id = update.effective_message.chat_id
    sender_id = update.effective_user.id
    print(f'SENDER ID {sender_id}')
    print(f'GRUP ID {group_chat_id}')
    bot.send_message(chat_id=sender_id, text=f'personal message to: {sender_id}')
    bot.send_message(chat_id=group_chat_id, text=f'universal message to: {group_chat_id}')

    bot.send_message(chat_id=group_chat_id, text=emojize("yummy :cake:", use_aliases=True))
    custom_keyboard = [[emojize(":tongue:", use_aliases=True),emojize(":boy:", use_aliases=True)], ]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)

    bot.send_message(chat_id=group_chat_id,
                     text="Custom Keyboard Test",
                     reply_markup=reply_markup)

    # Remove a custom keyboard
    # reply_markup = telegram.ReplyKeyboardRemove()
    # >> > bot.send_message(chat_id=chat_id, text="I'm back.", reply_markup=reply_markup)
    """Echo the user message."""
    raw_text = update.message.text
    print(f'RECEIVED MESSAGE::: {raw_text}')
    # if raw_text=='top-left':
    #     reply_markup = telegram.ReplyKeyboardRemove()
    #     bot.send_message(chat_id=chat_id, text="I'm back.", reply_markup=reply_markup)
    return
    splitting_val = raw_text.split()[0]

    try:
        val = float(splitting_val)
    except ValueError:
        val = None
        m_for_self = m_for_others = raw_text
    if isinstance(val, float):
        rest = update.message.text[len(splitting_val):]
        fname = update.message.chat.first_name
        lname = update.message.chat.last_name
        write_val(date=update.message.date,
                  name=f'{fname} {lname}',
                  val=val,
                  rest=rest)
        m_for_others = f'{fname} {lname} внес новую трату: {val}  на: "{rest}"'
        m_for_self = f'Ваша трата:  {val}  на: "{rest}" успешно зарегистрирована'
        update.message.reply_text(m_for_self)
    send_message(chat_id, m_for_others)


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def send_message(chat_id, text):
    print('AAAA', get_users())
    users = [p for p in get_users() if p != str(chat_id)]
    if users:
        for u in users:
            bot.sendMessage(chat_id=u, text=text, )


def new_members(bot, update):
    # here you receive a list of new members (User Objects) in a single service message
    new_members = update.message.new_chat_members
    # do your stuff here:
    for member in new_members:
        print(member.username)
def process_payment( update,context):
    print('RRRR',context.matches[0].group('amount'))
    print('AAAAA', context.matches[0].group('rest'))


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    # Get the dispatcher to register handlers

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    # we try to grasp all messages starting with digits here to process them as new records
    dp.add_handler(MessageHandler(Filters.regex(payment_regex), process_payment))

    # TODO: when new chat members are added - register them in the db

    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_members))
    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))
    # dp.add_handler(MessageHandler(Filters.all, smth))
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
