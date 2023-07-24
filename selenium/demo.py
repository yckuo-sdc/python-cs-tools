from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# The place we will direct our WebDriver to
url = 'https://www.tainan.gov.tw'

# Run Browser in background
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

service = Service('/usr/bin/chromedriver')

# Creating the WebDriver object using the ChromeDriver
driver = webdriver.Chrome(options=options,service=service)

# Directing the driver to the defined url
driver.get(url)
print(driver.title)
