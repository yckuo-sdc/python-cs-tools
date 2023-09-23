import os

import pandas as pd
from dotenv import load_dotenv

def concatenate_values(series):
    return ', '.join(series)

load_dotenv()
HOST = os.getenv('NOTICE_HOST')
USERNAME = os.getenv('NOTICE_USERNAME')
PASSWORD = os.getenv('NOTICE_PASSWORD')

# Specify the sheet name or index
PATH_TO_EXCEL = os.path.join(os.path.dirname(__file__), 'notice_excels',
                             'asusrt.xlsx')
SHEET1_NAME = '警訊內容'
SHEET2_NAME = '機關資訊'
SHEET3_NAME = '執行結果'

# If using openpyxl for .xlsx files
df1 = pd.read_excel(PATH_TO_EXCEL, engine='openpyxl', sheet_name=SHEET1_NAME)
df2 = pd.read_excel(PATH_TO_EXCEL, engine='openpyxl', sheet_name=SHEET2_NAME)

## Grouping by multiple columns
df2['port'] = df2['port'].astype(str)
grouped_data = df2.groupby('name')
df2 = grouped_data.agg({
    'ip': concatenate_values,
    'port': concatenate_values
}).reset_index()

form_inputs = df1.to_dict('records')
form_inputs = next(iter(form_inputs), None)
deparments = df2.to_dict('records')
print(deparments)
