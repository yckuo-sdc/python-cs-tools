"""Module Proof of Concept for CVE-2018-17020."""
import os
import socket
import sys

import pandas as pd
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import helper.function as func
import helper.http_validator as http
from package.ip2gov_adapter import Ip2govAdapter
from package.shodan_adapter import ShodanAdapter

ACCESSIBLE_CODES = [200]


def get_response_code(url, headers=""):
    try:
        if headers == "":
            headers = {
                'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            }
        # ignore verifying the SSL certificate
        response = requests.get(url,
                                headers=headers,
                                allow_redirects=True,
                                verify=False,
                                timeout=5)
        print(response.status_code)
        return response.status_code
    except Exception as e:
        print(e)
        return False


def is_accessible(request_url):
    """Function confirm that web field is accessible."""
    code = get_response_code(request_url)
    print(code)
    if code not in ACCESSIBLE_CODES:
        return False

    return True


if __name__ == '__main__':

    ip2gov = Ip2govAdapter()
    sa = ShodanAdapter()

    #search_filters = '19dec2003 DVR country:"tw" org:"Government Service Network (GSN)"'
    #search_filters = 'http.html:"19dec2003" org:"Government Service Network (GSN)"'
    #search_filters = 'http.html:"19dec2003" country:"tw"'
    #search_filters = '19dec2003 DVR country:"tw"'
    #search_filters = 'mini_httpd/1.19 19dec2003 org:"Government Service Network (GSN)"'
    #search_filters = '401 Unauthorized  Server: mini_httpd/1.19 19dec2003 country:"tw" org:"Government Service Network (GSN)"'
    #search_filters = '401 mini_httpd country:"tw" org:"Government Service Network (GSN)"'
    #search_filters = 'RTSP/1.0 200 OK country:"TW" org:"Government Service Network (GSN)"'
    search_filters = {
        'country': 'tw',
        'org': 'Government Service Network (GSN)',
        'all_no_quotes': 'RTSP/1.0 200 OK',
    }

    match_fields = [
        {
            'label': 'ip',
            'field': 'ip_str'
        },
        {
            'label': 'port',
            'field': 'port'
        },
        {
            'label': 'product',
            'field': 'product'
        },
        {
            'label': 'ssl',
            'field': 'ssl'
        },
        {
            'label': 'data',
            'field': 'data'
        },
    ]

    fields = sa.basic_query_cursor(search_filters, match_fields)
    #print(fields)
