from termcolor import colored
import shutil
from functools import wraps
from telegram import ChatAction
from budget.models import Payer

def cp(*x, color='red', center=True):
    columns = shutil.get_terminal_size().columns
    x = ' '.join([str(i) for i in x])
    if center:
        x = x.center(columns, '-')
    print(colored(x, color, 'on_cyan', attrs=['bold']))


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context, *args, **kwargs)

    return command_func



def get_user(from_user):
    user_id = from_user.id
    fname = from_user.first_name
    lname = from_user.last_name
    user_info = {'first_name': fname, 'last_name': lname}
    user, _ = Payer.objects.get_or_create(telegram_id=user_id, defaults=user_info)
    return user
