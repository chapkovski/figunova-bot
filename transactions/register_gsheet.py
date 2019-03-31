import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date, datetime
from json import dumps
from gspread.exceptions import CellNotFound, APIError
from commands import logging

logger = logging.getLogger('gsheet_registration_module')

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file",
          "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', SCOPES)

client = gspread.authorize(creds)
sheet = client.open("budget").sheet1


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def gsheet_register_payment(date, user_id, update_id, user_name, val, description, ):
    date = dumps(date, default=json_serial)
    row = [date, user_id, user_name, val, description, update_id]
    index = 2
    try:
        client = gspread.authorize(creds)
        sheet = client.open("budget").sheet1
        sheet.insert_row(row, index)
    except (CellNotFound, APIError):
        logger.warning('SOMETHING IS WRONG WITH PAYMENT REGISTRATION!!!!')
        return False


def delete_gsheet_record(update_id):
    try:
        client = gspread.authorize(creds)
        sheet = client.open("budget").sheet1
        cell = sheet.find(update_id)
        row_number = cell.row
        sheet.delete_row(row_number)
        return True
    except (CellNotFound, APIError):
        logger.warning('SOMETHING IS WRONG!!!!')
        return False

