"""Module Proof of Concept for CVE-2018-17020."""
import os
import socket

import pandas as pd
import requests

import helper.function as func
import helper.http_validator as http
from package.ip2gov_adapter import Ip2govAdapter
from package.shodan_adapter import ShodanAdapter

ACCESSIBLE_CODES = [200, 401]


def get_response_code(url):
    try:
        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
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
    if code not in ACCESSIBLE_CODES:
        return False

    return True


if __name__ == '__main__':

    ip2gov = Ip2govAdapter()
    sa = ShodanAdapter()

    path_to_csv = os.path.join(os.path.dirname(__file__), "data",
                               "use_cve_2023_20198.csv")

    results = []
    i = 0
    while True:
        results.append({'i': i})
        i = i + 1
        df = pd.DataFrame(results)
        with open(path_to_csv, 'a') as f:
            df.to_csv(f, header=False, index=False, encoding='utf-8-sig')
        #df.to_csv(path_to_csv, index=False, encoding='utf-8-sig')
        input('press')
