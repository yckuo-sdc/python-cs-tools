""" Automated Website Screenshot"""
import argparse
import os
import re
import sys
import urllib.parse

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


def convert_url_to_filename(target_url):
    """Function convert url to valid filename."""
    netloc = urllib.parse.urlparse(target_url).netloc
    path = urllib.parse.urlparse(target_url).path

    # Remove special characters and replace them with underscores
    filename = re.sub(r'[^\w\s.-]', '_', netloc + path)

    # Remove leading underscores and dashes
    filename = re.sub(r'^[_-]+', '', filename)

    # Remove trailing underscores and dashes
    filename = re.sub(r'[_-]+$', '', filename)

    return filename


def get_scroll_value(target_driver, attr):
    """Function get scroll value of attribute."""
    return target_driver.execute_script(
        'return document.body.parentNode.scroll' + attr)


parser = argparse.ArgumentParser()
parser.add_argument('--csv', help='Path to the csv (e.g. ./url.csv)')
parser.add_argument(
    '--shot-dir', help='Path to the screenshot directory (e.g. ./screenshots)')

args = parser.parse_args()

if args.csv is None:
    print('Path to csv must be provided (e.g. --csv ./url.csv)')
    sys.exit(0)

if args.shot_dir is None:
    print(
        'Path to screenshot directory must be provided (e.g. --shot-dir ./screenshots)'
    )
    sys.exit(0)

PATH_TO_CSV = os.path.join(os.path.dirname(__file__), args.csv)
PATH_TO_SHOT_DIR = os.path.join(os.path.dirname(__file__), args.shot_dir)

if __name__ == '__main__':

    df = pd.read_csv(PATH_TO_CSV)
    urls = df['url'].tolist()

    # Run Browser in background
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--ignore-certificate-errors')

    service = Service('/usr/bin/chromedriver')

    # Creating the WebDriver object using the ChromeDriver
    driver = webdriver.Chrome(options=options, service=service)

    # Setting an implicit wait of 2 seconds
    driver.implicitly_wait(2)

    #S = lambda X: driver.execute_script('return document.body.parentNode.scroll'+X)
    driver.set_window_size(get_scroll_value(driver, 'Width'),
                           get_scroll_value(driver, 'Height'))

    for url in urls:
        valid_filename = convert_url_to_filename(url) + '.png'
        path_to_shot = os.path.join(PATH_TO_SHOT_DIR, valid_filename)

        driver.get(url)
        driver.find_element(By.TAG_NAME, "body").screenshot(path_to_shot)
        print(url, driver.title)
