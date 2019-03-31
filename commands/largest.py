
def largest(update, context):
    try:
        how_many = int(context.args[0])
    except (IndexError, ValueError):
        how_many = 5
    try:
        raw_date = context.args[1]

    except IndexError:
        todayDate = datetime.datetime.now()
        raw_date = str(todayDate.replace(day=1))
    try:
        date = parser.parse(raw_date)
    except ValueError:
        update.message.reply_text(f'Чет какая-то поебота вместо даты, попробуй еще раз...')
        return
    user_id = update.message.from_user.id
    try:
        user = Payer.objects.get(telegram_id=user_id)
    except Payer.DoesNotExist:
        update.message.reply_text(f'Не могу найти никаких записей о тебе, чувак...')
        return
    date = date.replace(tzinfo=pytz.UTC)
    payments = Payment.objects.filter(creator=user, timestamp__gte=date).order_by('-amount')[:how_many]
    if payments.exists():
        message = f"""
         <b>Твои top-{how_many} трат с {date.strftime('%d-%m-%y')}:</b>\n"""
        for i, p in enumerate(payments):
            message += f"""{i + 1}. ({p.timestamp.strftime('%d-%m-%y')}) {p.description}: {p.amount}\n"""
        update.message.reply_html(text=message)
    else:
        update.message.reply_text(f'Никаких трат в этом периоде, везуха!')

