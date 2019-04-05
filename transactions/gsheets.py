import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date, datetime
from json import dumps
from gspread.exceptions import CellNotFound, APIError
from commands import logging

# todo: redo it in classes. DRY!

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file",
          "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('transactions/client_secret.json', SCOPES)

client = gspread.authorize(creds)
sheet = client.open("budget").sheet1

field_col_correspondence = {
    "timestamp": 1, "user_id": 2, "user_name": 3, "amount": 4, "description": 5, "update_id": 6, "category": 7,
}


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def register_payment(i):
    timestamp = dumps(i.timestamp, default=json_serial)
    if i.category:
        category = i.category.name
    else:
        category = ''
    user_name = f'{i.creator.first_name} {i.creator.last_name}'
    row = [timestamp, i.creator.telegram_id, user_name, i.amount, i.description, i.update, category]
    index = 2
    try:
        client = gspread.authorize(creds)
        sheet = client.open("budget").sheet1
        sheet.insert_row(row, index)
    except (CellNotFound, APIError):
        logger.error(f'Failed to register payment {i.update} in google sheets')
        return False


def delete_record(i):
    try:
        client = gspread.authorize(creds)
        sheet = client.open("budget").sheet1
        cell = sheet.find(i.update)
        row_number = cell.row
        sheet.delete_row(row_number)
        return True
    except (CellNotFound, APIError):
        logger.error(f'Failed to locate record {i.update} in google sheets')
        return False


def update_record(i):
    timestamp = dumps(i.timestamp, default=json_serial)
    user_name = f'{i.creator.first_name} {i.creator.last_name}'
    if i.category:
        category = i.category.name
    else:
        category = ''
    row = [timestamp, i.creator.telegram_id, user_name, i.amount, i.description, i.update, category]
    try:
        cell = sheet.find(i.update)
        row_number = cell.row
        for col_number, value in enumerate(row):
            sheet.update_cell(row_number, col_number + 1, value)
        return True
    except (CellNotFound, APIError):
        logger.error(f'Failed to locate record {i.update} in google sheets')
        return False
    except Exception as e:
        logger.error(e)
        return False