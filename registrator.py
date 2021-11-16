import os
# import pandas as pd
import gspread

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", 'https://spreadsheets.google.com/feeds']
GC = None

LOCAL_CREDENTIALS_FILE = "credentials_private.json"
SERVER_CREDENTIALS_FILE = "credentials.json"

def load_google_creds():
    load_creds(local=os.path.getsize(SERVER_CREDENTIALS_FILE) == 2)

def load_creds(local=False):
    global GC
    creds_file = LOCAL_CREDENTIALS_FILE if local else SERVER_CREDENTIALS_FILE
    GC = gspread.service_account(creds_file)

load_google_creds()

class Registrator:
    def __init__(self, sheets_id, use_rating=False):
        self.sheets_id = sheets_id
        self.use_rating = use_rating
        self.sheets = GC.open_by_key(sheets_id)

        if len(self.sheets.worksheets()) < 2:
            self.sheets.add_worksheet(title="Results", rows=100, cols=100)
        self.reg_sheet = self.sheets.get_worksheet(0)
        self.reg_sheet.update_title("Registration")
        self.res_sheet = self.sheets.get_worksheet(1)

        # self.format_sheets()
    
    def format_sheets(self):
        '''
        Add the correct column headers to the registration and results sheets.
        '''
        self.reg_sheet.clear()
        self.reg_sheet.update("A1:D1", [['ID', 'DiscordUserID', 'Name', 'Rating']])
        self.reg_sheet.format("A1:D1", {'textFormat': {'bold': True}})

        self.res_sheet.clear()
        self.res_sheet.update("A2:C2", [['Match', 'Winner', 'Loser']])
        self.res_sheet.format("A2:C2", {'textFormat': {'bold': True}})

    def add_registration(self, player: list):
        '''
        Add a player registration row to the registration sheet.
        '''
        if self.registration_exists(player):
            return ":x:", "You are already registered for this tournament."

        row_num = self.__get_next_available_row(self.reg_sheet)
        range = f"A{row_num}:D{row_num}"
        player = self.reformat_player(player, row_num-1)
        self.reg_sheet.update(range, player)
        
        return ":white_check_mark:", None
    
    def remove_registration(self, userID):
        '''
        Remove a player registration row from the registration sheet.
        '''
        cell = self.reg_sheet.find(userID, in_column=2)
        if not cell: # registration doesn't exist
            return ":x:", "You are not registered for this tournament."
        self.reg_sheet.delete_rows(cell.row)

        return ":white_check_mark:", None
    
    def __get_next_available_row(self, sheet: gspread.Worksheet):
        '''
        Find the next available row to insert a player registration.
        '''
        sheet_vals = sheet.get_values()
        return len(sheet_vals)+1
    
    @staticmethod
    def reformat_player(player: list, num):
        player.insert(0, num)
        return [player]
    
    def registration_exists(self, player):
        '''
        Check if player registration is already present in the registration sheet.
        '''
        user_id = player[0]
        return self.reg_sheet.find(user_id, in_column=2)

# if __name__ == "__main__":
#     sheet_id = "1I9Qt8UUanXh06P6J5-j2Vka8ddW7HUIiuhCR5F_iDyE"
#     reg = Registrator(sheet_id, use_rating=False)

#     reg.add_registration(['123912t30923', 'Zion Rao', None])
#     reg.remove_registration('123912t30923')
    







