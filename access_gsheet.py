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


def write_val(date, name, val, rest):
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
    row = [date, name, val, rest]
    index = 1
    sheet.insert_row(row, index)


def get_users():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file",
              "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', SCOPES)
    client = gspread.authorize(creds)
    #
    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    f = client.open("budget")
    worksheet = f.worksheet("Users")
    values_list = worksheet.col_values(1)
    return values_list


def register_user(user_id, first_name=None, last_name=None):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file",
              "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', SCOPES)
    client = gspread.authorize(creds)
    #
    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    f = client.open("budget")
    worksheet = f.worksheet("Users")
    try:
        cell = worksheet.find(str(user_id))
    except CellNotFound:

        index = 1
        row = [user_id, first_name, last_name]
        worksheet.insert_row(row, index)
    else:

        print('USER FOUND!', cell)
