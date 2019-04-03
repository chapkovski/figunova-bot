from commands.general import default
from telegram.ext import CallbackQueryHandler, ConversationHandler, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardRemove, ForceReply
from transactions.models import register_transaction, get_transaction_params
from commands.keyboards import storno_keyboard
import logging
from telegram.error import BadRequest

logger = logging.getLogger(__name__)
from commands.utils import get_user

WISH_STORNO_CONFIRMED, ENTERING_AMOUNT = range(2)


def cancel_due_to_inactivity(context):
    update = context.job.context
    try:
        context.bot.delete_message(message_id=update.message_id, chat_id=update.chat.id)
    except BadRequest:
        logger.warning('Message to delete has not been found')

    conversation_key = (update.chat.id, update.chat.id)
    storno_chat_handler.update_state(ConversationHandler.END, conversation_key)


def storno_start(update, context):
    user = get_user(update.message.from_user)
    logger.info(f'Getting storno request from {user.telegram_id}')
    r = update.message.reply_text(
        "Ты правда хочешь ввести возврат?! ",
        reply_markup=storno_keyboard())
    logger.info(r)
    j = context.job_queue
    j.run_once(cancel_due_to_inactivity, 5, context=r)
    return WISH_STORNO_CONFIRMED


def proceed_to_amount_storno(update, context):
    for j in context.job_queue.jobs():
        if j.name == 'cancel_due_to_inactivity':
            j.schedule_removal()
            logger.info('removing timeout job')
    user_id = update.callback_query.message.chat.id
    logger.info(f'Storno willigness confirmed by {user_id}')
    update.callback_query.message.reply_text(
        "Введи сумму и объяснение почему - для начальства",
        reply_markup=ForceReply())
    update.callback_query.message.delete()
    return ENTERING_AMOUNT


def register_storno(update, context):
    transaction_params = get_transaction_params(update, context)
    transaction_params['amount'] = -abs(float(transaction_params['amount']))
    transaction_params['description'] = 'STORNO ' + transaction_params['description']
    register_transaction(**transaction_params)
    amount = transaction_params['amount']
    user = transaction_params['user']
    update.message.reply_text(
        f"Я успешно зарегистрировал возврат на сумму {amount}. Пусть иные завидуют твоей бережливости, {user}!",
        reply_markup=ReplyKeyboardRemove())

    logger.info(f"successfuly entering storno at the amount of {amount} for user {user} ")
    return ConversationHandler.END


def cancel_storno(update, context):
    for j in context.job_queue.jobs():
        if j.name == 'cancel_due_to_inactivity':
            j.schedule_removal()
            logger.info('removing timeout job')
    logger.info('Storno operation is cancelled')
    update.callback_query.message.delete()
    update.callback_query.answer(text='')
    user_data = context.user_data
    user_data.clear()
    return ConversationHandler.END


def unclear_data(update, context):
    update.message.reply_text(text='Не могу понять что ты имеешь ввиду и на всякий случай осуществлю абортивную '
                                   'модернизацию')

    user_data = context.user_data
    user_data.clear()
    return ConversationHandler.END


storno_regex = r'^(?P<amount>[+-]?[0-9]+([,.][0-9]*)?) (?P<description>.+)$'
register_storno_handler = MessageHandler(Filters.regex(storno_regex), register_storno, pass_user_data=True)

storno_chat_handler = ConversationHandler(
    entry_points=[CommandHandler('storno', storno_start)],
    states={
        WISH_STORNO_CONFIRMED: [CallbackQueryHandler(proceed_to_amount_storno,
                                                     pattern=r'^proceed_to_storno$',
                                                     pass_user_data=True)],
        ENTERING_AMOUNT: [register_storno_handler, ],
        # ConversationHandler.TIMEOUT: [CallbackQueryHandler(unclear_data, pass_user_data=True)]
    },
    fallbacks=[CallbackQueryHandler(cancel_storno,
                                    pattern=r'^cancel_storno$',
                                    pass_user_data=True),
               MessageHandler(Filters.text, unclear_data, pass_user_data=True)
               ],
    conversation_timeout=10
)
