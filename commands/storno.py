
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