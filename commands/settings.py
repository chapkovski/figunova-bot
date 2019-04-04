from .keyboards import settings_keyboard
from .general import cancel_or_done
from .utils import get_user
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler
import logging

logger = logging.getLogger(__name__)
SET_CATEGORY_SHOWN = 1


def settings_start(update, context):
    user = get_user(update.message.from_user)
    context.user_data['user'] = user
    update.message.reply_text(
        "Ты хочешь указывать категорию при каждой трате?",
        reply_markup=settings_keyboard(user))

    return SET_CATEGORY_SHOWN


def set_categories(update, context):
    logger.info('Ready to set new option in users setting')
    user = context.user_data['user']
    logger.info(user)
    new_val = bool(int(context.match.groupdict()['cat_answer']))
    user.show_cats = new_val
    user.save()
    update.callback_query.message.edit_reply_markup()

    return ConversationHandler.END


settings_chat_handler = ConversationHandler(
    entry_points=[CommandHandler('settings', settings_start)],
    states={
        SET_CATEGORY_SHOWN: [CallbackQueryHandler(set_categories,
                                                  pattern=r'^show_cat_option_(?P<cat_answer>\d+)$',
                                                  pass_user_data=True), ],
    },
    fallbacks=[],
)