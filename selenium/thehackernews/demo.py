from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import requests

## Start a headless Chrome browser using Selenium
#chrome_options = Options()
#chrome_options.add_argument("--headless")  # Run headless mode, no GUI
#service = Service('/usr/bin/chromedriver')  # Specify the path to your ChromeDriver executable
#driver = webdriver.Chrome(service=service, options=chrome_options)
#
## Navigate to the URL
url = 'https://thehackernews.com/2024/01/syrian-hackers-distributing-stealthy-c.html'
#driver.get(url)
#
## Wait for JavaScript to render (adjust sleep time as needed)
#time.sleep(5)
#
## Get the rendered HTML content
#rendered_html = driver.page_source
#
## Close the browser
#driver.quit()

# Now you can process the rendered HTML as needed, for example, you can use requests to post-process it
#response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'})
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'})
#response = requests.get(url)
original_html = response.text

# Do something with the rendered HTML content
#print("Rendered HTML:", rendered_html)

# Do something with the original HTML content (without rendering JavaScript)
print("Original HTML:", original_html)
