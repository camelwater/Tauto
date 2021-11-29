import os
from typing import List
import gspread, gspread.utils

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", 'https://spreadsheets.google.com/feeds']
GC = None

LOCAL_CREDENTIALS_FILE = "resources/credentials_private.json"
SERVER_CREDENTIALS_FILE = "resources/credentials.json"

def get_google_creds():
    return load_creds(local=os.path.getsize(SERVER_CREDENTIALS_FILE) == 2)

def load_creds(local=False):
    creds_file = LOCAL_CREDENTIALS_FILE if local else SERVER_CREDENTIALS_FILE
    return gspread.service_account(creds_file)

GC = get_google_creds()

class Registrator:
    def __init__(self, sheets_id, use_rating=False):
        self.sheets_id = sheets_id
        self.use_rating = use_rating
    
    def setup_sheets(self):
        sheets = GC.open_by_key(self.sheets_id)

        self.reg_sheet = sheets.get_worksheet(0)
        self.reg_sheet.update_title("Registration")
        try:
            self.res_sheet = sheets.worksheet("Results")
        except:
            self.res_sheet = sheets.add_worksheet(title="Results", rows=100, cols=100)
        
        self.format_sheets()


    def format_sheets(self):
        '''
        Add the correct column headers to the registration and results sheets.
        '''
        # self.reg_sheet.clear()
        self.reg_sheet.update("A1:D1", [['ID', 'DiscordUserID', 'Name', 'Rating']])
        self.reg_sheet.format("A1:D1", {'textFormat': {'bold': True}})

        self.res_sheet.clear()

    def add_registration(self, player: list, force: bool = False):
        '''
        Add a player registration row to the registration sheet.
        '''
        # if not self.formatted:
        #     self.format_sheets()
        #     self.formatted = True

        if not force and self.registration_exists(player):
            return "❌", "You are already registered for this tournament."

        row_num = self.__get_next_row(self.reg_sheet)
        range = f"A{row_num}:D{row_num}"
        player = self.reformat_player(player, row_num-1)
        self.reg_sheet.update(range, player)
        
        return "✅", None
    
    def remove_registration(self, userID):
        '''
        Remove a player registration row from the registration sheet.
        '''
        cell = self.reg_sheet.find(str(userID), in_column=2)
        if not cell: # registration doesn't exist
            return "❌", "You are not registered for this tournament."
        self.reg_sheet.delete_rows(cell.row)

        return "✅", None
    
    def load_registrations(self):
        '''
        Return all player registrations from registration sheet as a list of lists.
        '''
        last_row = self.__get_next_row(self.reg_sheet)-1
        range = f"A2:D{last_row}"
        return self.reg_sheet.get_values(range)
    
    def add_round_results(self, results: list):
        '''
        Add a round's results to the results sheet.
        '''
        round_title = results[0]
        results_data = results[1]

        title_range, results_range = self.__get_next_results_range(len(results_data))
        title_values = [[round_title], ["Match", "Winner", "Loser"]]

        self.res_sheet.update(title_range, title_values)
        self.res_sheet.format(title_range, {'textFormat': {'bold': True}})

        self.res_sheet.update(results_range, results_data)
    
    @staticmethod
    def __get_next_row(sheet: gspread.Worksheet):
        '''
        Find the next available row to insert a row.
        '''
        sheet_vals = sheet.get_values()
        return len(sheet_vals)+1
    
    def __get_next_results_range(self, num_entries: int):
        '''
        Find the next available range to insert a round's results.
        '''
        sheet_vals = self.res_sheet.get_values(major_dimension='COLUMNS')
        start_col = len(sheet_vals) + (1 if len(sheet_vals) == 0 else 2)
        end_col = start_col+3
        start_row = 1
        end_row = start_row+2+num_entries
        range_start = gspread.utils.rowcol_to_a1(start_row+2, start_col)
        range_end = gspread.utils.rowcol_to_a1(end_row, end_col)
        title_start = gspread.utils.rowcol_to_a1(start_row, start_col)
        title_end = gspread.utils.rowcol_to_a1(start_row+1, end_col)

        title_range = f"{title_start}:{title_end}"
        results_range = f"{range_start}:{range_end}"

        return title_range, results_range

    
    @staticmethod
    def reformat_player(player: list, num):
        player.insert(0, num)
        return [player]
    
    def registration_exists(self, player):
        '''
        Check if player registration is already present in the registration sheet.
        '''
        user_id = player[0]
        return self.reg_sheet.find(str(user_id), in_column=2)

# if __name__ == "__main__":
#     sheet_id = "1I9Qt8UUanXh06P6J5-j2Vka8ddW7HUIiuhCR5F_iDyE"
#     reg = Registrator(sheet_id, use_rating=False)

#     reg.add_registration(['123912t30923', 'Zion Rao', None])
#     reg.remove_registration('123912t30923')