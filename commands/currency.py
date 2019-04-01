from .constants import pop_currencies, regex_pop_currencies
from .keyboards import currency_keyboard
from .general import cancel_or_done
from .utils import get_user
from telegram import ForceReply
from exceptions import NoSuchCurrency
from budget.models import CurrencyQuote
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters
import logging

logger = logging.getLogger(__name__)
CHOOSING_CURRENCY, CURRENCY_INPUT = range(2)


def currency_start(update, context):
    update.message.reply_text(
        "Выбери валюту в которой ты хочешь вести учет",
        reply_markup=currency_keyboard())

    return CHOOSING_CURRENCY


def custom_currency_choice(update, context):
    update.message.reply_text("Введите название валюты (три буквы типа USD, EUR. Если что - спросите у Фильки.",
                              reply_markup=ForceReply())
    return CURRENCY_INPUT


def check_register_currency(update, context):
    user = get_user(update.message.from_user)
    date = update.effective_message.date
    currency_name = update.message.text.upper()
    logger.info(f'User with id {user.telegram_id} made a request to change currency to {currency_name}  @ {date}.')
    if currency_name != 'RUB':
        try:
            quote = CurrencyQuote.get_quote(currency_name)
        except NoSuchCurrency:
            update.message.reply_text("Не могу найти название валюты. Попробуйте RUB или спросите у Фильки",
                                      reply_markup=ForceReply())
            return CURRENCY_INPUT
        else:
            msg = f"Теперь все твои траты будут считаться в {currency_name} по курсу {quote} рублей"
    else:
        msg = "Считаем отныне все в старых добрых рублях"

    user.currencies.create(name=currency_name)
    update.message.reply_text(msg)
    logger.info(f'Currency name successfully changed to {currency_name} for user with id {user.telegram_id} @ {date}.')
    return ConversationHandler.END



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
        CHOOSING_CURRENCY: [popular_currency_handler,
                            custom_choice_handler,
                            ],
        CURRENCY_INPUT: [currency_input_handler],
    },
    fallbacks=[done_handler],
)
