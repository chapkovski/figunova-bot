"""# we try to grasp all messages starting with digits here to process them as new records"""

# this is the regex to catch payments
payment_regex = r'(?P<amount>[0-9]+([,.][0-9]*)?) (?P<description>.+)'
from .utils import send_typing_action
from transactions.models import get_transaction_params, register_transaction
from telegram.ext import MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
from .keyboards import cat_keyboard
import logging
from budget.models import Payment, Category
from telegram.error import BadRequest

logger = logging.getLogger(__name__)
CATEGORY_TO_ADD = 1


def cancel_due_to_inactivity(context):
    update = context.job.context
    try:
        context.bot.edit_message_reply_markup(message_id=update.message_id, chat_id=update.chat.id)
    except BadRequest:
        logger.warning('Message to delete has not been found')

    conversation_key = (update.chat.id, update.chat.id)
    payment_chat_handler.update_state(ConversationHandler.END, conversation_key)


@send_typing_action
def register_payment(update, context):
    logger.info('get a new payment info')
    transaction_params = get_transaction_params(update, context)

    success = register_transaction(**transaction_params)
    r = update.message.reply_text(success, quote=False, reply_markup=cat_keyboard())
    j = context.job_queue
    j.run_once(cancel_due_to_inactivity, 5, context=r)
    transaction_params.pop('date')
    payment = Payment.objects.get(**transaction_params)
    context.user_data['transaction'] = payment
    logger.info('Successfully register a new payment, proceed to categories...')
    return CATEGORY_TO_ADD


def register_category(update, context):
    for j in context.job_queue.jobs():
        if j.name == 'cancel_due_to_inactivity':
            j.schedule_removal()
            logger.info('removing timeout job')
    cat_id = context.match.groupdict()['cat_id']
    cat = Category.objects.get(pk=cat_id)
    transaction = context.user_data['transaction']
    transaction.category = cat
    transaction.save()
    logger.info('Successfully register new category for current transaction')
    update.callback_query.message.reply_text(
        f'Пометил себе трату "{transaction.amount} на {transaction.description}" как {cat.description}', quote=False)
    update.callback_query.message.delete()

    return ConversationHandler.END


def unclear_data(update, context):
    logger.info('User started typing withoug choosing category...')

    user_data = context.user_data
    user_data.clear()
    return ConversationHandler.END


payment_handler = MessageHandler(Filters.regex(payment_regex), register_payment, pass_user_data=True)
payment_chat_handler = ConversationHandler(
    entry_points=[payment_handler],
    states={
        CATEGORY_TO_ADD: [CallbackQueryHandler(register_category,
                                               pattern=r'^cat_id_(?P<cat_id>\d+)$',
                                               pass_user_data=True)],
    },
    fallbacks=[
        MessageHandler(Filters.text, unclear_data, pass_user_data=True)
    ],
    # conversation_timeout=10
)
