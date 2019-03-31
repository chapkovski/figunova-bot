def cancel_or_done(update, context):
    user_data = context.user_data
    user_data.clear()
    update.message.reply_text("\U0001F44D", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def help_processor(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_html(help_message)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def cancel(update, context):
    user_data = context.user_data
    ReplyKeyboardRemove()
    return ConversationHandler.END


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

help_message = '''
    Привет! Я - бот, который регистирует все наши траты. \n
    Если тебе надо ввести новую трату просто введи сумму а потом ее описание. \n
    Если хочется посмотреть отчет о тратах и среднюю сумму которую каждый из нас тратит в день набери 
    <code>/report</code>. По умолчанию отчет будет с первого числа этого месяца. \n
    Если тебе надо вывести отчет, начиная с другой даты, набери <code>/report 01.01.2018</code> - получишь отчет с 1 
    января 2018 года (или с любой другой даты :) ).
    \n Если  хочешь получить справку по командам (я буду добавлять новые...), то набери <code>/help</code>
    '''


def start(update, context):
    """Send a message when the command /start is issued."""

    update.message.reply_html(help_message)
