""" Automated Notice Project """
import argparse
import os
import sys
from datetime import datetime
from string import Template

import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

def strip_whitespace(origin_df):
    """Function strip whitespace from all values in a Pandas DataFrame."""
    return origin_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

def find_files_with_name(directory, target_name):
    """Function confirm that file is existed."""
    for file in os.listdir(directory):
        if file.find(target_name) == 0:
            return os.path.join(directory, file)
    return False


def get_department_file_path(directory, department_name):
    """Function get file path with department name."""
    file_type_orders = ['zip', 'csv', 'png', 'jpg']

    for file_type in file_type_orders:
        file_name = f"{department_name}.{file_type}"
        file_path = find_files_with_name(directory, file_name)
        if file_path:
            return file_path

    return False


def concatenate_values(series):
    """Function concatenate the list."""
    filtered_series_strings = [
        str(item) for item in series if str(item) != 'nan'
    ]
    unique_filtered_series_strings = list(set(filtered_series_strings))
    return ', '.join(unique_filtered_series_strings)


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
    load_dotenv()
    HOST = os.getenv('NOTICE_HOST', 'http://10.3.40.19:8000')
    USERNAME = os.getenv('NOTICE_USERNAME')
    PASSWORD = os.getenv('NOTICE_PASSWORD')

    # Specify the sheet name or index
    SHEET1_NAME = '警訊內容'
    SHEET2_NAME = '機關資訊'
    SHEET3_NAME = '執行結果'

    # If using openpyxl for .xlsx files
    df1 = pd.read_excel(PATH_TO_EXCEL,
                        engine='openpyxl',
                        sheet_name=SHEET1_NAME)
    df2 = pd.read_excel(PATH_TO_EXCEL,
                        engine='openpyxl',
                        sheet_name=SHEET2_NAME)

    # Strip whitespace from all values
    df1 = strip_whitespace(df1)
    df2 = strip_whitespace(df2)

    inputs = df1.to_dict('records')
    inputs = next(iter(inputs), None)

    grouped_data = df2.groupby('department_name')
    if 'ioc_ip' in df2:
        df2 = grouped_data.agg({
            'department_ip': concatenate_values,
            'ioc_ip': concatenate_values,
        }).reset_index()
    else:
        df2 = grouped_data.agg({
            'department_ip': concatenate_values,
        }).reset_index()

    records = df2.to_dict('records')

    # Attachment validation
    if inputs['notice.attachment'] == '有':
        for record in records:
            record['file_path'] = get_department_file_path(
                PATH_TO_ATTACH_DIR, record['department_name'])
            if not record['file_path']:
                sys.exit(
                    f"Exit: Can't find attachment: {record['department_name']}"
                )

    print(inputs)
    print(records)
    input("Press Enter to continue...")

    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--ignore-certificate-errors')

    service = Service('/usr/bin/chromedriver')

    # Creating the WebDriver object using the ChromeDriver
    driver = webdriver.Chrome(options=options, service=service)

    # Setting an implicit wait of 2 seconds
    driver.implicitly_wait(2)

    # ============
    # Part1. login
    # ============

    # Directing the driver to the defined url
    driver.get(HOST)
    print(driver.title)

    # Clear field to empty it from any previous data
    driver.find_element(By.NAME, "systemUser.account").clear()
    driver.find_element(By.NAME, "systemUser.password").clear()

    # Enter Text
    driver.find_element(By.NAME, "systemUser.account").send_keys(USERNAME)
    driver.find_element(By.NAME, "systemUser.password").send_keys(PASSWORD)

    # Click on the element
    driver.find_element(By.XPATH, "//input[@type='submit']").click()

    execution_results = []
    for record in records:

        # =====================
        # Part2. Classification
        # =====================

        print(record['department_name'])

        # Directing the driver to the defined url
        driver.get(f"{HOST}/notice/Notice.do?method:publishNoticeStep1")

        # noticeCategoryid = {0: '警訊', 2: '國際通報'}
        select_element = driver.find_element(By.NAME, "noticeCategoryid")
        select = Select(select_element)
        select.select_by_visible_text(inputs['noticeCategoryid'])

        # typeId = {1: 'EWA', 3: 'DEF', 4: 'INT', 5: 'ANA'}
        select_element = driver.find_element(By.NAME, "typeId")
        select = Select(select_element)
        select.select_by_visible_text(inputs['typeId'])

        # eventId = {'165': '其他'}
        select_element = driver.find_element(By.NAME, "eventId")
        select = Select(select_element)
        select.select_by_visible_text(inputs['eventId'])

        driver.find_element(By.XPATH, "//input[@type='submit']").click()

        # ==============
        # Part3. Filling
        # ==============

        subject = Template(inputs['notice.subject']).substitute(
            department_name=record['department_name'])
        content = Template(inputs['notice.content']).substitute(
            department_ip=record['department_ip'])
        suggestion = inputs['notice.suggestion']
        reference = inputs['notice.reference']
        ips = record['department_ip'].split(", ")

        # notice.source = ['外部資安組織', '本院自行發現', 'GSN威脅情蒐機制']
        select_element = driver.find_element(By.NAME, "notice.source")
        select = Select(select_element)
        select.select_by_visible_text(inputs['notice.source'])

        today = datetime.now().strftime("%Y-%m-%d")
        driver.find_element(By.NAME, "detectTime").send_keys(today)
        driver.find_element(By.NAME, "notice.subject").send_keys(subject)

        # notice.severity = ['高', '中', '低']
        select_element = driver.find_element(By.NAME, "notice.severity")
        select = Select(select_element)
        select.select_by_visible_text(inputs['notice.severity'])

        # notice.restriction = ['公開資訊', '群組資訊', '機密資訊']
        select_element = driver.find_element(By.NAME, "notice.restriction")
        select = Select(select_element)
        select.select_by_visible_text(inputs['notice.restriction'])

        driver.find_element(By.NAME, "notice.content").send_keys(content)

        if inputs['typeId'] == 'INT':
            driver.find_element(By.NAME, "notice.approach").send_keys(
                inputs['notice.approach'])

        if 'ioc_ip' in record:
            select_element = driver.find_element(By.CLASS_NAME, "select_ipdn")
            select = Select(select_element)
            select.select_by_visible_text("IP")
            select_element = driver.find_element(By.CLASS_NAME,
                                                 "select_malicioustype")
            select = Select(select_element)
            select.select_by_visible_text("惡意CandC與下載站")

            ioc_ips = record['ioc_ip'].split(", ")
            for ioc_ip in ioc_ips:
                driver.find_element(By.XPATH,
                                    "//input[@id='ioc']").send_keys(ioc_ip)
                driver.execute_script("addMal()")

        for ip in ips:
            driver.find_element(By.XPATH, "//input[@id='ip']").send_keys(ip)
            driver.execute_script("add()")

        driver.find_element(By.NAME, "notice.suggestion").send_keys(suggestion)
        driver.find_element(By.NAME, "notice.reference").send_keys(reference)

        if inputs['notice.attachment'] == '有':
            driver.find_element(By.NAME,
                                "myFile").send_keys(record['file_path'])
            driver.find_element(By.XPATH, "//input[@type='submit']").click()

        # ==============
        # Part4. Preview
        # ==============
        input("Press Enter to continue...")

        driver.find_element(By.XPATH, "//input[@type='submit']").click()

        # ==========================
        # Part5. Search Organization
        # ==========================

        # Clear all recipients
        driver.get(f"{HOST}/notice/NoticePrePublish!deleteAllTo.do")

        driver.execute_script("goToSelectToPage()")
        driver.find_element(By.ID, "NoticePrePublish_search").send_keys(
            record['department_name'])
        driver.find_element(By.ID, "NoticePrePublish_normal_query").click()

        # ===========================
        # Part6. Add Email Recipients
        # ===========================
        checkboxes = driver.find_elements(By.XPATH,
                                          "//input[@name='selectGroup']")

        # Iterate through the checkboxes and click each one
        for checkbox in checkboxes:
            checkbox.click()

        try:
            driver.find_element(By.ID, "NoticePrePublish_normal_ok").click()
        except NoSuchElementException:
            input(
                "The element: 'NoticePrePublish_normal_ok' was not found on the web page"
                ", press Enter to continue...")

        td = driver.find_element(By.XPATH, "//table/tbody/tr[1]/td[1]")
        notice_id = td.text

        execution_results.append(record | {'notice_id': notice_id})

        # ==============
        # Part7. Publish
        # ==============
        input("Press Enter to continue...")
        try:
            publish_button = driver.find_element(
                By.XPATH, "//tr[last()]//input[@type='submit']")
            publish_button.click()
        except NoSuchElementException:
            input("The element: 'publish button' was not found on the web page"
                  ", press Enter to continue...")
        #input("Press Enter to continue...")

        # Write the modified DataFrame back to the worksheet
        execution_results_df = pd.DataFrame(execution_results)
        with pd.ExcelWriter(PATH_TO_EXCEL,
                            engine='openpyxl',
                            mode='a',
                            if_sheet_exists='replace') as writer:
            execution_results_df.to_excel(writer,
                                          sheet_name=SHEET3_NAME,
                                          index=False)
