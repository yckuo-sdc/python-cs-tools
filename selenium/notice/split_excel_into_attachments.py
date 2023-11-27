""" Selenium Project """
import argparse
import os
import sys

import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--excel', help='Path to the excel (e.g. ./excel.xlsx)')
parser.add_argument(
    '--attach-dir',
    help='Path to the attachment directory (e.g. ./attachments)')

args = parser.parse_args()

if args.excel is None:
    print('Path to excel must be provided (e.g. --excel ./notice.xlsx)')
    sys.exit(0)

if args.attach_dir is None:
    print(
        'Path to attachment directory must be provided (e.g. --attach-dir ./attachments)'
    )
    sys.exit(0)

PATH_TO_EXCEL = os.path.join(os.path.dirname(__file__), args.excel)
PATH_TO_ATTACH_DIR = os.path.join(os.path.dirname(__file__), args.attach_dir)

if __name__ == '__main__':

    SHEET1_NAME = '警訊內容'
    SHEET2_NAME = '機關資訊'
    SHEET3_NAME = '執行結果'

    # If using openpyxl for .xlsx files
    df = pd.read_excel(PATH_TO_EXCEL,
                       engine='openpyxl',
                       sheet_name=SHEET2_NAME)

    # Group the DataFrame by 'Category'
    grouped = df.groupby('department_name')

    # Get all group names
    group_names = grouped.groups.keys()

    # Print the group names
    group_names = list(group_names)

    for group_name in group_names:
        print(group_name)
        df_group_name = grouped.get_group(group_name)
        path_to_csv = os.path.join(PATH_TO_ATTACH_DIR, f"{group_name}.csv")
        df_group_name.to_csv(path_to_csv, index=False, encoding='utf-8-sig')
