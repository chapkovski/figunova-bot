
@send_typing_action
def register_payment(update, context):
    transaction_params = get_transaction_params(update, context)
    success = register_transaction(**transaction_params)
    update.message.reply_text(success, quote=False)
