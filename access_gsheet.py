import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread.models import CellNotFound
from datetime import date, datetime

from json import dumps


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def gsheet_register_payment(date,user_id, user_name, val, rest, ):
    date = dumps(date, default=json_serial)

    # use creds to create a client to interact with the Google Drive API
    # scope = ['https://spreadsheets.google.com/feeds']
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file",
              "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', SCOPES)
    client = gspread.authorize(creds)
    #
    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open("budget").sheet1
    #
    # Extract and print all of the values
    row = [date, user_id, user_name, val, rest]
    index = 2
    sheet.insert_row(row, index)


