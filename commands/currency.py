
def currency_start(update, context):
    reply_keyboard = [pop_currencies,
                      ['Другая валюта'],
                      ['Отмена']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text(
        "Выбери валюту в которой ты хочешь вести учет",
        reply_markup=markup)

    return CurrencyChatChoices.choosing_currency


def custom_currency_choice(update, context):
    update.message.reply_text("Введите название валюты (три буквы типа USD, EUR. Если что - спросите у Фильки.",
                              reply_markup=ForceReply())
    return CurrencyChatChoices.input


def check_register_currency(update, context):
    currency_name = update.message.text.upper()
    if currency_name != 'RUB':
        try:
            quote = CurrencyQuote.get_quote(currency_name)
        except NoSuchCurrency:
            update.message.reply_text("Не могу найти название валюты. Попробуйте RUB или спросите у Фильки",
                                      reply_markup=ForceReply())
            return CurrencyChatChoices.input
    user = get_user(update.message.from_user)
    user.currencies.create(name=currency_name)
    if currency_name != 'RUB':
        update.message.reply_text(f"Теперь все твои траты будут считаться в {currency_name} по курсу {quote} рублей")
    else:
        update.message.reply_text(f"Считаем отныне все в старых добрых рублях")
    return cancel_or_done(update, context)
