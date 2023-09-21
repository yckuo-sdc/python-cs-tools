""" Selenium Project """
import os
from datetime import datetime
from string import Template

import pandas as pd
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

load_dotenv()
HOST = os.getenv("NOTICE_HOST")
USERNAME = os.getenv("NOTICE_USERNAME")
PASSWORD = os.getenv("NOTICE_PASSWORD")

# Specify the sheet name or index
PATH_TO_EXCEL = os.path.join(os.path.dirname(__file__), 'notice_excels', 'asusrt.xlsx')
SHEET1_NAME = '警訊內容'
SHEET2_NAME = '機關資訊'

# If using openpyxl for .xlsx files
df1 = pd.read_excel(PATH_TO_EXCEL, engine='openpyxl', sheet_name=SHEET1_NAME)
df2 = pd.read_excel(PATH_TO_EXCEL, engine='openpyxl', sheet_name=SHEET2_NAME)

form_inputs = df1.to_dict('records')
form_inputs = next(iter(form_inputs), None)
deparments = df2.to_dict('records')
print(form_inputs)
print(deparments)

## Run Browser in background
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

# Directing the driver to the defined url

### Page 1. Login ###
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

for deparment in deparments:
    ### Page 2. Classification ###
    driver.get(f"{HOST}/notice/Notice.do?method:publishNoticeStep1")

    select_element = driver.find_element(By.NAME, "noticeCategoryid")
    select = Select(select_element)
    select.select_by_value('0')

    select_element = driver.find_element(By.NAME, "typeId")
    select = Select(select_element)
    select.select_by_value('1')

    select_element = driver.find_element(By.NAME, "eventId")
    select = Select(select_element)
    select.select_by_value('165')

    driver.find_element(By.XPATH, "//input[@type='submit']").click()

    ### Page 3. Filling ###
    subject = Template(form_inputs['subject']).substitute(department_name=deparment['name'])
    content = Template(form_inputs['content']).substitute(department_ip=deparment['ip'])
    suggestion = form_inputs['suggestion']
    reference = form_inputs['reference']
    ips = deparment['ip'].split(",")

    select_element = driver.find_element(By.NAME, "notice.source")
    select = Select(select_element)
    select.select_by_value('本院自行發現')

    today = datetime.now().strftime("%Y-%m-%d")
    driver.find_element(By.NAME, "detectTime").send_keys(today)
    driver.find_element(By.NAME, "notice.subject").send_keys(subject)

    select_element = driver.find_element(By.NAME, "notice.severity")
    select = Select(select_element)
    select.select_by_value('低')

    select_element = driver.find_element(By.NAME, "notice.restriction")
    select = Select(select_element)
    select.select_by_value('機密資訊')

    driver.find_element(By.NAME, "notice.content").send_keys(content)

    for ip in ips:
        driver.find_element(By.XPATH, "//input[@id='ip']").send_keys(ip)
        driver.execute_script("add()")

    driver.find_element(By.NAME, "notice.suggestion").send_keys(suggestion)
    driver.find_element(By.NAME, "notice.reference").send_keys(reference)

    # Specify the path to the file you want to upload
    file_path = os.path.join(os.path.dirname(__file__), 'attachments/asusrt', deparment['upload_file'])
    driver.find_element(By.NAME, "myFile").send_keys(file_path)
    driver.find_element(By.XPATH, "//input[@type='submit']").click()

    ### Page 4. Preview ###
    #driver.find_element(By.XPATH, "//input[@type='submit']").click()

    input("Press Enter to continue...")
