from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup)
from .constants import pop_currencies


def delete_keyboard(items):
    """ Return keyboard with buttons to delete one item."""
    if not items.exists():
        return None
    delete_buttons_row = []
    for i, j in enumerate(items):
        delete_buttons_row.append(InlineKeyboardButton(f'{i + 1}', callback_data=f'delete_update_{j.update}'))
    cancel_row = [InlineKeyboardButton('Отмена', callback_data='cancel_delete')]
    return InlineKeyboardMarkup([delete_buttons_row, cancel_row])


def users_keyboard(users):
    """ Return keyboard with user names to show a graph for specific user."""
    if not users.exists():
        return None
    rows = []
    for i in users:
        rows.append(InlineKeyboardButton(f'{i.first_name} {i.last_name}',
                                         callback_data=f'telegram_id_{i.telegram_id}'))

    cancel_row = [InlineKeyboardButton('Отмена', callback_data='cancel')]
    return InlineKeyboardMarkup([rows, cancel_row])


def storno_keyboard():
    """ Keyboard to confirm storno action."""

    rows = [InlineKeyboardButton('Да, очень, я вся горю!', callback_data='proceed_to_storno')]
    cancel_row = [InlineKeyboardButton('Отмена', callback_data='cancel_storno')]
    return InlineKeyboardMarkup([rows, cancel_row])


def currency_keyboard():
    reply_keyboard = [pop_currencies,
                      ['Другая валюта'],
                      ['Отмена']]
    return ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
