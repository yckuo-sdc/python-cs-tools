#!/usr/bin/python3 
import requests

SUCCESS_CODES = range(200, 300)  # 200-299

def get_response_code(url):  
    try:
        r = requests.head(url, allow_redirects=True, timeout=10)
        return r.status_code
    except Exception as e:
        print(e)
        return False

def is_successful(url):
    code = get_response_code(url)
    if not code:
        return False
   
    #print(code)
    if code not in SUCCESS_CODES: 
        return False

    return True


if __name__ == '__main__':  
    url_list = [
        'https://stackoverflow.com',
        'http://web.yckuo.nics/phpmyadmin-nics',
        'http://web.yckuo.nics',
    ]

    for url in url_list:
	    print(is_successful(url))
