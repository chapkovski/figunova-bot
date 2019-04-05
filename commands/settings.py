from .keyboards import settings_keyboard
from .general import cancel_or_done
from .utils import get_user
from telegram.ext import (ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, Filters)
import logging
from telegram.error import BadRequest

logger = logging.getLogger(__name__)
SET_CATEGORY_SHOWN = 1


def cancel_due_to_inactivity(context):
    update = context.job.context
    try:
        context.bot.editMessageText(message_id=update.message_id, chat_id=update.chat.id,
                                    text='ну ладно,  передайте слонихе что Эдик приходил!')
    except BadRequest:
        logger.warning('Message to delete has not been found')

    conversation_key = (update.chat.id, update.chat.id)
    settings_chat_handler.update_state(ConversationHandler.END, conversation_key)


def settings_start(update, context):
    user = get_user(update.message.from_user)
    context.user_data['user'] = user
    r = update.message.reply_text(
        "Ты хочешь указывать категорию при каждой трате?",
        reply_markup=settings_keyboard(user))
    j = context.job_queue
    j.run_once(cancel_due_to_inactivity, 5, context=r)
    return SET_CATEGORY_SHOWN


def set_categories(update, context):
    for j in context.job_queue.jobs():
        if j.name == 'cancel_due_to_inactivity':
            j.schedule_removal()
            logger.info('removing timeout job')
    logger.info('Ready to set new option in users setting')
    user = context.user_data['user']
    logger.info(user)
    new_val = bool(int(context.match.groupdict()['cat_answer']))
    user.show_cats = new_val
    user.save()
    update.callback_query.message.edit_reply_markup()
    cat_corr = {False: "не", True: ""}
    update.callback_query.message.reply_text(
        f'Ну оки, {cat_corr[new_val]} буду показывать категории после ввода новой траты')
    return ConversationHandler.END


def unclear_data(update, context):
    update.message.reply_text(text='Не могу понять что ты имеешь ввиду и на всякий случай осуществлю абортивную '
                                   'модернизацию')

    user_data = context.user_data
    user_data.clear()
    return ConversationHandler.END


settings_chat_handler = ConversationHandler(
    entry_points=[CommandHandler('settings', settings_start)],
    states={
        SET_CATEGORY_SHOWN: [CallbackQueryHandler(set_categories,
                                                  pattern=r'^show_cat_option_(?P<cat_answer>\d+)$',
                                                  pass_user_data=True), ],
    },
    fallbacks=[MessageHandler(Filters.text, unclear_data, pass_user_data=True)],
)
