import os

import pandas as pd

IMPORT_FILE_NAME = 'ngnix_ingress_controller.xlsx'
EXPORT_DIR_NAME = 'ngnix_ingress_controller'

# Specify the sheet name or index
PATH_TO_EXCEL = os.path.join(os.path.dirname(__file__), 'notices', 'excels',
                             IMPORT_FILE_NAME)
SHEET1_NAME = '警訊內容'
SHEET2_NAME = '機關資訊'
SHEET3_NAME = '執行結果'

# If using openpyxl for .xlsx files
df = pd.read_excel(PATH_TO_EXCEL, engine='openpyxl', sheet_name=SHEET2_NAME)

# Group the DataFrame by 'Category'
grouped = df.groupby('name')

# Get all group names
group_names = grouped.groups.keys()

# Print the group names
group_names = list(group_names)
directory = os.path.join(os.path.dirname(__file__), 'notices', 'attachments', EXPORT_DIR_NAME)

for group_name in group_names:
    print(group_name)
    df_group_name = grouped.get_group(group_name)
    path_to_csv = os.path.join(directory, f"{group_name}.csv")
    df_group_name.to_csv(path_to_csv, index=False, encoding='utf-8-sig')
