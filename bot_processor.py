# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bot that registers the payments.
"""

print('hello! budget bot is running...')

from handler_funs import (start, delete, report, largest, register_payment, receive_delete_msg,
                          cancel_or_done, currency_start, chart_start, individual_chart, error,
                          check_register_currency, custom_currency_choice,
                          storno_enter_amount, storno_start)
import django
from os import environ
from constants import CurrencyChatChoices, regex_pop_currencies, StornoChatChoices

django.setup()
import logging

from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
# TOKEN = environ.get('TELEGRAM_API')
TOKEN = '617288510:AAHS0ghER8QZPt7WN-fu-bNDe6WN4sIDj_Y'  # TODO: Temporarily - switching to reserve bot for testing

"""Start the bot."""

updater = Updater(TOKEN,
                  use_context=True)
dp = updater.dispatcher
bot = updater.bot
# this is the regex to catch payments
payment_regex = r'(?P<amount>[0-9]+([,.][0-9]*)?) (?P<description>.+)'

""" 
When somebody sends the request \delete we get him 5 last messages and inline keyboard to choose
which one to delete.
When he clicks on the button, the message id of callback data is passed back and the item is deleted.
The answer_callback_query reposnds a notification.
Previous message (with list of 5 last items) is deleted(??)
 
  """


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
                                  cancel_or_done,
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

    ########### BLOCK: CHARTS ##############################################################
    charts_start_handler = CommandHandler('chart', chart_start)
    individual_chart_handler = CallbackQueryHandler(individual_chart, pattern=r'^telegram_id_(?P<telegram_id>\d+)$', )
    ############ END OF: CHARTS #############################################################

    ########### BLOCK: STORNO ##############################################################
    storno_chat_handler = ConversationHandler(
        entry_points=[CommandHandler('storno', storno_start)],
        states={
            StornoChatChoices.confirming: [
                CallbackQueryHandler(go_to_storno_registration, pattern=r'^proceed_to_storno$', pass_user_data=True),

            ],
            StornoChatChoices.entering_amount: [MessageHandler(Filters.regex(payment_regex),
                                                               storno_enter_amount, pass_user_data=True)],
        },
        fallbacks=[done_handler]

    )


############ END OF: STORNO #############################################################

handlers = [
    start_handler,
    charts_start_handler,
    individual_chart_handler,
    help_handler,
    delete_handler,
    callback_delete_handler,
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
updater.idle()

if __name__ == '__main__':
    main()
