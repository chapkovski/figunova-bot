from access_gsheet import gsheet_register_payment, delete_gsheet_record
from utils import cp, send_typing_action
from keyboards import users_keyboard, delete_keyboard, storno_keyboard
from constants import CurrencyChatChoices, pop_currencies, StornoChatChoices

import django
from dateutil import parser
from django.db.models.functions import Concat
from django.db.models import CharField, Value as V
from telegram import (ReplyKeyboardMarkup, ForceReply, ReplyKeyboardRemove)
import pytz
import datetime
from django.db.models import Sum, Min, Max

django.setup()
from budget.models import Payment, Payer, CurrencyQuote
from budget.exceptions import NoSuchCurrency
from read_lenin import get_lenin_answer
import logging
from emoji import emojize
from telegram.ext import ConversationHandler
from charts import IndividualChart

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


def get_user(from_user):
    user_id = from_user.id
    fname = from_user.first_name
    lname = from_user.last_name
    user_info = {'first_name': fname, 'last_name': lname}
    user, _ = Payer.objects.get_or_create(telegram_id=user_id, defaults=user_info)
    return user


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


def report(update, context):
    if context.args:
        try:
            date = parser.parse(context.args[0])
        except ValueError:
            update.message.reply_text(f'Не могу распознать дату, попробуйте еще раз...')
            return
    else:
        todayDate = datetime.datetime.now()
        date = todayDate.replace(day=1, hour=0, minute=0)
    date = date.replace(tzinfo=pytz.UTC)
    payments = Payment.objects.order_by().filter(timestamp__gte=date)
    if payments.exists():
        minmaxpayments = payments.aggregate(Min('timestamp'), Max('timestamp'))
        numdays = (minmaxpayments['timestamp__max'] - minmaxpayments['timestamp__min']).days + 1
        payments = payments.annotate(
            screen_name=Concat('creator__first_name', V(' '), 'creator__last_name',
                               output_field=CharField()), ). \
            values('screen_name').annotate(total_sum=Sum('amount'), avg_sum=(Sum('amount') / numdays))

        message = f"""<b>Траты начиная с {date.strftime('%d-%m-%y')}:</b>\n"""
        for p in payments:
            message += f"""<i>{p['screen_name']}</i>: Всего: <b>{round(p['total_sum'],
                                                                       0)}</b>. В среднем за день: {round(p['avg_sum'],
                                                                                                          0)}\n"""
        update.message.reply_html(text=message)
    else:
        update.message.reply_text(f'Нет трат за этот период!')


def start(update, context):
    """Send a message when the command /start is issued."""

    update.message.reply_html(help_message)


def register_transaction(date, amount, description, user, update_id):
    rate = user.get_rate()
    val = round(float(amount) * rate, 2)
    currency_name = user.get_current_currency()
    """Connect to DB and register new payment there."""

    Payment.objects.create(amount=val,
                           description=description,
                           creator=user,
                           update=update_id
                           )
    gsheet_register_payment(date=date,
                            user_id=user.telegram_id,
                            user_name=f'{user.first_name} {user.last_name}',
                            val=val,
                            description=description,
                            update_id=update_id)
    foreign_val = f'{amount} {currency_name}; ' if currency_name != 'RUB' else ''
    if user.telegram_id == '344416307':  # TODO just a joke - remove later
        lenin_answer = get_lenin_answer()
    else:
        lenin_answer = ''
    logger.info(f'{user.telegram_id} payment for {foreign_val} or {val} @ {date}.')
    success = emojize(f':white_check_mark: ({foreign_val}{val} рублей) {lenin_answer}', use_aliases=True)
    return success


def get_transaction_params(update, context):
    d = {'date': update.effective_message.date,
         'update_id': update.update_id,
         'user': get_user(update.message.from_user),
         'amount': context.match.groupdict().get('amount'),
         'description': context.match.groupdict().get('description')
         }
    return d


@send_typing_action
def register_payment(update, context):
    transaction_params = get_transaction_params(update, context)
    success = register_transaction(**transaction_params)
    update.message.reply_text(success, quote=False)


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


def receive_delete_msg(update, context):
    if update.callback_query.data == 'cancel':
        logger.info('отмена удаления')
    else:
        try:
            update_id = update.callback_query.data
            Payment.objects.filter(update=update_id).delete()
            delete_gsheet_record(update_id)
        except Payment.DoesNotExist:
            update.message.reply_html('что-то пошло не так. Спросите у фильки')
    update.callback_query.answer(show_alert=False, text="Пыщь!")
    update.callback_query.message.delete()


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


def cancel_or_done(update, context):
    user_data = context.user_data
    user_data.clear()
    update.message.reply_text("\U0001F44D", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


########### BLOCK: CHART HANDLES ##############################################################
def chart_start(update, context):
    payers = Payer.objects.all()
    kb = users_keyboard(payers)
    update.message.reply_text(text="Выбери про кого ты хочешь ВСЕ узнать", reply_markup=kb, )


def individual_chart(update, context):
    telegram_id = context.match.groupdict()['telegram_id']
    chart = IndividualChart(telegram_id)
    update.callback_query.message.reply_photo(chart.get_url(), quote=False)
    update.callback_query.message.delete()


############ END OF: CHART HANDLES #############################################################

########### BLOCK: STORNO HANDLERS ##############################################################

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

############ END OF: STORNO HANDLERS #############################################################
