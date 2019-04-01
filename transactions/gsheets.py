import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date, datetime
from json import dumps
from gspread.exceptions import CellNotFound, APIError
from commands import logging

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file",
          "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('transactions/client_secret.json', SCOPES)

client = gspread.authorize(creds)
sheet = client.open("budget").sheet1


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def gsheet_register_payment(date, user_id, update_id, user_name, val, description, ):
    date = dumps(date, default=json_serial)
    row = [date, user_id, user_name, val, description, update_id]
    index = 2
    try:
        client = gspread.authorize(creds)
        sheet = client.open("budget").sheet1
        sheet.insert_row(row, index)
    except (CellNotFound, APIError):
        logger.error('Failed to register payment in google sheets')
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
        logger.error('Failed to delete record in google sheets')
        return False

