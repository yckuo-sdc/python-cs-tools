#!/usr/bin/python3 
from urllib.parse import urlparse
from bs4 import BeautifulSoup
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

def find_text_on_tags(html_doc, text): 
    soup = BeautifulSoup(html_doc, 'html.parser')
    matched_tags = soup.find_all(lambda tag: len(tag.find_all()) == 0 and text.lower() in tag.get_text().lower())

    for matched_tag in matched_tags:
        print("Matched: {}".format(matched_tag))

    if len(matched_tags) > 0:
        return True

    return False

def is_routing_to_error_page(url):
    try:
        error_msgs = ['404', 'not found', 'invalid', '失效', '無效', '不存在']
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}
        r = requests.get(url, headers=headers, allow_redirects=False, timeout=10)
        for error_msg in error_msgs:
            if find_text_on_tags(r.text, error_msg):
                print('It is routing to error page')
                return True
        return False 
    except Exception as e:
        print(e)
        return False
    
def is_routing_to_homepage(url):
    obj = urlparse(url)
    if obj.path == "" and obj.params == "" and obj.query == "" and obj.fragment == "":
        return False

    homepage = obj.scheme + '://' + obj.netloc
    print(homepage, url)
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}
        homepage_footprint = hashlib.sha1(requests.get(homepage, headers=headers, allow_redirects=True, timeout=10).text.encode('utf-8')).hexdigest() 
        url_footprint = hashlib.sha1(requests.get(url, headers=headers, allow_redirects=False, timeout=10).text.encode('utf-8')).hexdigest() 

        #print(homepage_footprint, url_footprint)

        if homepage_footprint == url_footprint:
            print('It is routing to homepage')
            return True

        return False 
    except Exception as e:
        print(e)
        return False

def is_custom_error_handling(url):
    if is_routing_to_homepage(url):
        return True
    if is_routing_to_error_page(url):
        return True
    
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
        if is_custom_error_handling(url):
            return False

    return True


if __name__ == '__main__':  

    html_doc = """
    <div>
        <p>This is 404 some text.</p>
        <p>Another paragraph With Target Text.</p>
    </div>
    """
    text = "404"
    find_text_on_tags(html_doc, text)

    url_list = [
        'https://stackoverflow.com',
        'http://web.yckuo.nics/phpmyadmin-nics',
        #'http://web.yckuo.nics',
        'https://www.programiz.com/python-programming/methods/string/random_path',
        #'https://www.tainan.gov.tw/random_path.aspx',
        'https://www.nics.nat.gov.tw/random_path.test',
        #'https://web.ksu.edu.tw/error/404.aspx',
    ]

    for url in url_list:
        print(url)
        print(is_successful(url))
        #print(is_routing_to_error_page(url))
