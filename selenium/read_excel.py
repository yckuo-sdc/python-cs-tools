import pandas as pd

# Specify the sheet name or index
PATH_TO_EXCEL = 'notice_samples.xlsx'
SHEET1_NAME = '警訊內容' 
SHEET2_NAME = '機關資訊'

# If using openpyxl for .xlsx files
df1 = pd.read_excel(PATH_TO_EXCEL, engine='openpyxl', sheet_name=SHEET1_NAME)
df2 = pd.read_excel(PATH_TO_EXCEL, engine='openpyxl', sheet_name=SHEET2_NAME)

form_inputs = df1.to_dict('records')
form_inputs = next(iter(form_inputs), None)
deparment_data = df2.to_dict('records')
print(form_inputs)
print(deparment_data)
