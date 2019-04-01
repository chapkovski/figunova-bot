"""# we try to grasp all messages starting with digits here to process them as new records"""

# this is the regex to catch payments
payment_regex = r'(?P<amount>[0-9]+([,.][0-9]*)?) (?P<description>.+)'
from .utils import send_typing_action
from transactions.models import get_transaction_params, register_transaction
from telegram.ext import MessageHandler, Filters


@send_typing_action
def register_payment(update, context):
    transaction_params = get_transaction_params(update, context)
    success = register_transaction(**transaction_params)
    update.message.reply_text(success, quote=False)


payment_handler = MessageHandler(Filters.regex(payment_regex), register_payment, pass_user_data=True)
