# !/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'budget_telebot.settings')
django.setup()
from telegram.ext import Updater
from commands import logging
from commands.charts import chart_chat_handler
from commands.general import start_handler, help_handler,error
from commands.delete import delete_chat_handler
from commands.largest import largest_handler
from commands.register_payment import payment_handler
from commands.report import report_handler
from commands.currency import currency_chat_handler
from commands.storno import storno_chat_handler
"""
Bot that registers the payments and does some reporting on them. It also can manage (delete, correct) the exsisting
payment records, and check if a user meets their financial goals.
"""

logger = logging.getLogger(__name__)

# Initializing django to access models.


TOKEN = os.environ.get('TELEGRAM_API')
# TOKEN = '617288510:AAHS0ghER8QZPt7WN-fu-bNDe6WN4sIDj_Y'  # TODO: Temporarily - switching to reserve bot for testing

logger.info('Starting the bot...')

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher


def main():
    handlers = [
        start_handler,
        chart_chat_handler,
        delete_chat_handler,
        help_handler,
        largest_handler,
        report_handler,
        currency_chat_handler,
        storno_chat_handler,
        payment_handler
    ]
    for handler in handlers:
        dp.add_handler(handler)

    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    logger.info('Hello! budget bot is running...')
    updater.idle()


if __name__ == '__main__':
    main()
