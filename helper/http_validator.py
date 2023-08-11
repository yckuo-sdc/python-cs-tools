#!/usr/bin/python3 
import requests

SUCCESS_CODES = range(200, 300)  # 200-299

def is_custom_error_page(url):
    try:
        error_msgs = ['404', 'not found', 'invalid', '失效', '不存在']
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}
        r = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
        for error_msg in error_msgs:
            if r.text.find(error_msg) >= 0:
                return True

        return False 
    except Exception as e:
        print(e)
        return False
    

def get_response_code(url):  
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}
        r = requests.head(url, headers=headers, allow_redirects=True, timeout=10)
        return r.status_code
    except Exception as e:
        print(e)
        return False

def is_successful(url):
    code = get_response_code(url)
    if not code:
        return False
   
    if code not in SUCCESS_CODES: 
        return False

    if code == 200:
        if is_custom_error_page(url):
            return False

    return True


if __name__ == '__main__':  
    url_list = [
        'https://stackoverflow.com',
        'http://web.yckuo.nics/phpmyadmin-nics',
        'http://web.yckuo.nics',
        'https://www.programiz.com/python-programming/methods/string/error_test',
    ]

    for url in url_list:
	    print(is_successful(url))
