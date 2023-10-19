""" Selenium Project """
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


def find_files_with_name(directory, target_name):
    """Function confirm that file is existed."""
    for file in os.listdir(directory):
        if file.find(target_name) == 0:
            return os.path.join(directory, file)
    return False


def concatenate_values(series):
    """Function concatenate the list."""
    return ', '.join(series)


load_dotenv()
HOST = os.getenv('NOTICE_HOST')
USERNAME = os.getenv('NOTICE_USERNAME')
PASSWORD = os.getenv('NOTICE_PASSWORD')

profile = {
    # cve_2023_20198
    'import_file_name': 'cve_2023_20198_int.xlsx',
    'import_dir_name': 'cve_2023_20198_int',
}

# Specify the sheet name or index
PATH_TO_EXCEL = os.path.join(os.path.dirname(__file__), 'notices', 'excels',
                             profile.get('import_file_name'))

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
print(form_inputs)
print(deparments)

attach_directory = os.path.join(os.path.dirname(__file__), 'notices',
                                'attachments', profile.get('import_dir_name'))
for deparment in deparments:
    file_name = f"{deparment['name']}.csv"
    file_path = find_files_with_name(attach_directory, file_name)
    print(file_path)
    if not file_path:
        sys.exit(f"Exit: Can't find attachment: {file_name}")
    deparment['file_path'] = file_path

#sys.exit(0)

### Run Browser in background
options = webdriver.ChromeOptions()
#options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--ignore-certificate-errors')

service = Service('/usr/bin/chromedriver')

# Creating the WebDriver object using the ChromeDriver
driver = webdriver.Chrome(options=options, service=service)

# Setting an implicit wait of 2 seconds
driver.implicitly_wait(2)

### Part 1. Login ###
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
for deparment in deparments:
    ### Part 2. Classification ###
    print(deparment['name'])

    # Directing the driver to the defined url
    driver.get(f"{HOST}/notice/Notice.do?method:publishNoticeStep1")

    # noticeCategoryid = {0: '警訊', 2: '國際通報'}
    select_element = driver.find_element(By.NAME, "noticeCategoryid")
    select = Select(select_element)
    select.select_by_value('0')

    # typeId = {1: 'EWA', 3: 'DEF', 4: 'INT', 5: 'ANA'}
    select_element = driver.find_element(By.NAME, "typeId")
    select = Select(select_element)
    select.select_by_value('4')

    # eventId = {159: '系統入侵'}
    select_element = driver.find_element(By.NAME, "eventId")
    select = Select(select_element)
    select.select_by_value('159')

    driver.find_element(By.XPATH, "//input[@type='submit']").click()

    ### Part 3. Filling ###
    subject = Template(
        form_inputs['subject']).substitute(department_name=deparment['name'])
    content = Template(
        form_inputs['content']).substitute(department_ip=deparment['ip'])
    approach = form_inputs['approach']
    suggestion = form_inputs['suggestion']
    reference = form_inputs['reference']
    ips = deparment['ip'].split(", ")

    # notice.source = ['外部資安組織', '本院自行發現', 'GSN威脅情蒐機制']
    select_element = driver.find_element(By.NAME, "notice.source")
    select = Select(select_element)
    select.select_by_value('本院自行發現')

    today = datetime.now().strftime("%Y-%m-%d")
    driver.find_element(By.NAME, "detectTime").send_keys(today)
    driver.find_element(By.NAME, "notice.subject").send_keys(subject)

    # notice.severity = ['高', '中', '低']
    select_element = driver.find_element(By.NAME, "notice.severity")
    select = Select(select_element)
    select.select_by_value('高')

    # notice.restriction = ['公開資訊', '群組資訊', '機密資訊']
    select_element = driver.find_element(By.NAME, "notice.restriction")
    select = Select(select_element)
    select.select_by_value('機密資訊')

    driver.find_element(By.NAME, "notice.content").send_keys(content)
    driver.find_element(By.NAME, "notice.approach").send_keys(approach)

    for ip in ips:
        driver.find_element(By.XPATH, "//input[@id='ip']").send_keys(ip)
        driver.execute_script("add()")

    driver.find_element(By.NAME, "notice.suggestion").send_keys(suggestion)
    driver.find_element(By.NAME, "notice.reference").send_keys(reference)

    # Specify the path to the file you want to upload
    driver.find_element(By.NAME, "myFile").send_keys(deparment['file_path'])
    driver.find_element(By.XPATH, "//input[@type='submit']").click()

    input("Press Enter to continue...")

    #### Part 4. Preview ###
    driver.find_element(By.XPATH, "//input[@type='submit']").click()

    #### Part 5. Search Address ###

    # Clear all recipients
    driver.get(f"{HOST}/notice/NoticePrePublish!deleteAllTo.do")

    driver.execute_script("goToSelectToPage()")
    driver.find_element(By.ID,
                        "NoticePrePublish_search").send_keys(deparment['name'])
    driver.find_element(By.ID, "NoticePrePublish_normal_query").click()

    #### Part 6. Add Address ###
    checkboxes = driver.find_elements(By.XPATH, "//input[@name='selectGroup']")

    # Iterate through the checkboxes and click each one
    for checkbox in checkboxes:
        checkbox.click()

    try:
        driver.find_element(By.ID, "NoticePrePublish_normal_ok").click()
    except NoSuchElementException:
        input(
            "The element: 'NoticePrePublish_normal_ok' was not found on the web page, Press Enter to continue..."
        )

    td = driver.find_element(By.XPATH, "//table/tbody/tr[1]/td[1]")
    notice_id = td.text

    execution_results.append(deparment | {'notice_id': notice_id})

    ### Final. Publish ###
    input("Press Enter to continue...")
    driver.find_element(By.XPATH, "//input[@type='submit']").click()

# Write the modified DataFrame back to the worksheet
execution_results_df = pd.DataFrame(execution_results)
with pd.ExcelWriter(PATH_TO_EXCEL,
                    engine='openpyxl',
                    mode='a',
                    if_sheet_exists='replace') as writer:
    execution_results_df.to_excel(writer, sheet_name=SHEET3_NAME, index=False)
