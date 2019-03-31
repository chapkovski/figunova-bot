"""
When somebody sends the request \delete we get him 5 last messages and inline keyboard to choose
which one to delete.
When he clicks on the button, the message id of callback data is passed back and the item is deleted.
The answer_callback_query reposnds a notification.
Previous message (with list of 5 last items) is deleted(??)

"""


def receive_delete_msg(update, context):
    if update.callback_query.data == 'cancel':
        logger.info('Deletion is cancelled.')
    else:
        try:
            update_id = update.callback_query.data
            Payment.objects.filter(update=update_id).delete()
            delete_gsheet_record(update_id)
        except Payment.DoesNotExist:
            update.message.reply_html('что-то пошло не так. Спросите у фильки')
    update.callback_query.answer(show_alert=False, text="Пыщь!")
    update.callback_query.message.delete()


def delete(update, context):
    n = 5
    user_id = update.message.from_user.id
    try:
        user = Payer.objects.get(telegram_id=user_id)
    except Payer.DoesNotExist:
        update.message.reply_text('Не могу найти никаких записей о тебе, чувак...')
        return
    last_n = Payment.objects.filter(creator=user)[:n]
    kb = delete_keyboard(last_n)
    if last_n.exists():
        message = f"""
         <b>Выбери что удалить:</b>    
         """
        for i, p in enumerate(last_n):
            message += f"""
             {i + 1}. ({p.timestamp.strftime('%d-%m-%y')}) {p.description}: {p.amount}
            """
        update.message.reply_html(text=message, reply_markup=kb, )
    else:
        update.message.reply_text(f'Чет не могу найти последних трат. Спроси у фильки что за хуйня')
    if update.callback_query:
        update.callback_query.answer()
