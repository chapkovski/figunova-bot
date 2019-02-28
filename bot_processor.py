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

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Chat

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
get_users()


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


def echo(update, context):
    """Echo the user message."""
    raw_text = update.message.text
    splitting_val = raw_text.split()[0]
    chat_id = update.effective_message.chat_id
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



def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def send_message(chat_id, text):
    print('AAAA', get_users())
    users = [p for p in get_users() if p != str(chat_id)]
    if users:
        for u in users:
            updater.bot.sendMessage(chat_id=u, text=text, )


def callback_func(bot, update):
    # here you receive a list of new members (User Objects) in a single service message
    new_members = update.message.new_chat_members
    # do your stuff here:
    for member in new_members:
        print(member.username)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary

    # Get the dispatcher to register handlers

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, callback_func))
    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

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
