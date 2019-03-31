def chart_start(update, context):
    payers = Payer.objects.all()
    kb = users_keyboard(payers)
    update.message.reply_text(text="Выбери про кого ты хочешь ВСЕ узнать", reply_markup=kb, )


def individual_chart(update, context):
    telegram_id = context.match.groupdict()['telegram_id']
    chart = IndividualChart(telegram_id)
    update.callback_query.message.reply_photo(chart.get_url(), quote=False)
    update.callback_query.message.delete()