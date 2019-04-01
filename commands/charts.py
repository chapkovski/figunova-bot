from budget.models import Payer
from .keyboards import users_keyboard
from charts import IndividualChartWithTrend
from .general import default
from telegram.ext import CallbackQueryHandler, CommandHandler, ConversationHandler
import logging
from commands.utils import get_user

logger = logging.getLogger(__name__)

GET_CHART = 0


def chart_start(update, context):
    user = get_user(update.message.from_user)
    logger.info(f'User with id {user.telegram_id} requested charts')
    payers = Payer.objects.all()
    kb = users_keyboard(payers)
    update.message.reply_text(text="Выбери про кого ты хочешь ВСЕ узнать", reply_markup=kb, )
    return GET_CHART


def individual_chart(update, context):
    telegram_id = context.match.groupdict()['telegram_id']
    chart = IndividualChartWithTrend(telegram_id)
    update.callback_query.message.reply_photo(chart.get_url(), quote=False)
    update.callback_query.message.delete()
    return ConversationHandler.END


charts_start_handler = CommandHandler('chart', chart_start)
individual_chart_handler = CallbackQueryHandler(individual_chart, pattern=r'^telegram_id_(?P<telegram_id>\d+)$', )

chart_chat_handler = ConversationHandler(
    entry_points=[CommandHandler("chart", chart_start)],
    states={
        GET_CHART: [individual_chart_handler],
    },
    fallbacks=[CallbackQueryHandler(default)],

)
