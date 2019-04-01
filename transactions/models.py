from commands.utils import get_user
from budget.models import Payment
from lenin import get_lenin_answer
from commands import logging

logger = logging.getLogger('transaction_module')
from emoji import emojize
from .gsheets import gsheet_register_payment


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
    logger.info(f'User with id {user.telegram_id} made payment for {foreign_val} {val} roubles @ {date}.')
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
