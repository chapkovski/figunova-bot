import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread.models import CellNotFound
from datetime import date, datetime
from utils import cp
from json import dumps
from gspread.exceptions import CellNotFound, APIError

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


def gsheet_register_payment(date, user_id, update_id, user_name, val, rest, ):
    date = dumps(date, default=json_serial)
    #    # Extract and print all of the values
    row = [date, user_id, user_name, val, rest, update_id]
    index = 2
    try:
        client = gspread.authorize(creds)
        sheet = client.open("budget").sheet1
        sheet.insert_row(row, index)
    except (CellNotFound, APIError):
        cp('SOMETHING IS WRONG WITH PAYMENT REGISTRATION!!!!')
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
        cp('SOMETHING IS WRONG!!!!')
        return False


if __name__ == '__main__':
    delete_gsheet_record('jpa')
