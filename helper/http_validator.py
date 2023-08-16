#!/usr/bin/python3 
from urllib.parse import urlparse
import requests
import hashlib
import re

SUCCESS_CODES = range(200, 300)  # 200-299

def is_bot_useragent(useragent):
    pattern = '\([^)]+\)|\S+\/'
    result = re.findall(pattern, useragent)
    useragent_count = len(result)
    print('{}: {}'.format(useragent, useragent_count))
    if useragent_count <= 5:
      return True
    return False

def is_custom_error_page(url):
    try:
        error_msgs = ['404', 'not found', 'invalid', '失效', '無效', '不存在']
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}
        r = requests.get(url, headers=headers, allow_redirects=False, timeout=10)
        for error_msg in error_msgs:
            if re.search(error_msg, r.text, re.IGNORECASE):
                print('It is custom error page')
                return True

        return False 
    except Exception as e:
        print(e)
        return False
    
def is_same_footprint_with_homepage(url):
    s = hashlib.sha1()
    obj = urlparse(url)
    homepage = obj.scheme + '://' + obj.netloc
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}
        homepage_footprint = hashlib.sha256(requests.get(homepage, headers=headers, allow_redirects=True, timeout=10).text.encode('utf-8')).hexdigest() 
        url_footprint = hashlib.sha256(requests.get(url, headers=headers, allow_redirects=False, timeout=10).text.encode('utf-8')).hexdigest() 

        print(homepage_footprint, url_footprint)

        if homepage_footprint == url_footprint:
            print('It is same footprint with homepage')
            return True

        return False 
    except Exception as e:
        print(e)
        return False

def get_response_code(url):  
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}
        r = requests.head(url, headers=headers, allow_redirects=False, timeout=10)
        return r.status_code
    except Exception as e:
        print(e)
        return False

def is_successful(url):
    code = get_response_code(url)
    print(code)
    if not code:
        return False
   
    if code not in SUCCESS_CODES: 
        return False

    if code == 200:
        if is_same_footprint_with_homepage(url):
            return False
        if is_custom_error_page(url):
            return False

    return True


if __name__ == '__main__':  
    url_list = [
        'https://stackoverflow.com',
        'http://web.yckuo.nics/phpmyadmin-nics',
        'http://web.yckuo.nics',
        'https://www.programiz.com/python-programming/methods/string/random_path',
        'https://www.tainan.gov.tw/random_path.aspx',
        'https://www.nics.nat.gov.tw/random_path.test',
    ]

    for url in url_list:
        print(url)
        print(is_successful(url))
