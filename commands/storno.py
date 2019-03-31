
def storno_start(update, context):
    update.message.reply_text(
        "Ты правда хочешь ввести возврат?! ",
        reply_markup=storno_keyboard())
    return StornoChatChoices.entering_amount


def storno_enter_amount(update, context):
    transaction_params = get_transaction_params(update, context)
    transaction_params['amount'] = -abs(float(transaction_params['amount']))
    register_transaction(**transaction_params)
    update.message.reply_text(
        "Я успешно зарегистрировал возврат. Пусть иные завидуют твоей бережливости, %USERNAME%!",
        reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END