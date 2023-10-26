from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

# The place we will direct our WebDriver to
url = 'https://www.tainan.gov.tw'
url = 'https://www.nics.nat.gov.tw/.htm'

urls = [
    'http://210.241.99.254:80',
    'http://61.60.10.65:80',
    'http://210.241.29.105:80',
    'http://210.241.72.161:80',
]

# Run Browser in background
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
# Replace with your desired width and height
driver.set_window_size(1920, 1080)

for url in urls:
    o = urlparse(url)
    filename = f"{o.netloc.replace('.', '_').replace(':', '_')}.png"
    # Directing the driver to the defined url
    driver.get(url)
    print(driver.title)
    driver.find_element(By.TAG_NAME, "body").screenshot(filename)

print("end...")
