from commands.utils import get_user
from budget.models import Payment
from lenin import get_lenin_answer
from commands import logging

logger = logging.getLogger('transaction_module')
from emoji import emojize
from .gsheets import gsheet_register_payment


def register_transaction(date, amount, description, creator, update):
    rate = creator.get_rate()
    val = round(float(amount) * rate, 2)
    currency_name = creator.get_current_currency()
    """Connect to DB and register new payment there."""

    Payment.objects.create(amount=val,
                           description=description,
                           creator=creator,
                           update=update
                           )
    gsheet_register_payment(date=date,
                            user_id=creator.telegram_id,
                            user_name=f'{creator.first_name} {creator.last_name}',
                            val=val,
                            description=description,
                            update_id=update)
    foreign_val = f'{amount} {currency_name}; ' if currency_name != 'RUB' else ''
    if creator.telegram_id == '344416307':  # TODO just a joke - remove later
        lenin_answer = get_lenin_answer()
    else:
        lenin_answer = ''
    logger.info(f'User with id {creator.telegram_id} made payment for {foreign_val} {val} roubles @ {date}.')
    success = emojize(f':white_check_mark: ({foreign_val}{val} рублей) {lenin_answer}', use_aliases=True)
    return success


def get_transaction_params(update, context):
    d = {'date': update.effective_message.date,
         'update': update.update_id,
         'creator': get_user(update.message.from_user),
         'amount': context.match.groupdict().get('amount'),
         'description': context.match.groupdict().get('description')
         }
    return d
