# import libraries
import os
from dotenv import load_dotenv
import ast
import gspread
import pandas as pd


def main():
    # get environment variables
    load_dotenv()
    GSPREAD_CREDENTIALS = ast.literal_eval(os.environ.get('GSPREAD_CREDENTIALS'))
    GSPREAD_AUTHORIZED_USERS = ast.literal_eval(os.environ.get('GSPREAD_AUTHORIZED_USERS'))

    # access gspread api
    gc, authorized_user = gspread.oauth_from_dict(GSPREAD_CREDENTIALS, GSPREAD_AUTHORIZED_USERS)

    # open google spreadsheet
    sh = gc.open('creator-link')
    worksheet = sh.worksheet('Sheet1')
    
    df_creator_link = pd.read_csv('./data/creator-link.csv')
    worksheet.update([df_creator_link.columns.values.tolist()] + df_creator_link.values.tolist())
    

if __name__ == '__main__':
    main()