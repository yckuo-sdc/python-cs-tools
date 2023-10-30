"""Module Proof of Concept for CVE-2023-20198."""
import datetime
import os
import sys

import pandas as pd
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

ACCESSIBLE_CODES = [200]

def get_response_code(url):
    """Functions"""
    try:
        headers = {
            'user-agent':
            'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/115.0.0.0 safari/537.36'
        }
        # ignore verifying the ssl certificate
        response = requests.get(url,
                                headers=headers,
                                allow_redirects=True,
                                verify=False,
                                timeout=5)
        return response.status_code
    except Exception as e:
        print(e)
        return None

def is_hexadecimal_string(input_string):
    """Function"""
    # Check if the input string is not empty
    if len(input_string) == 0:
        return False

    # Check if the input string contains only hexadecimal characters (0-9, a-f, A-F)
    return all(
        char.isalnum() and char.isnumeric() or 'a' <= char.lower() <= 'f'
        for char in input_string)


def is_accessible(request_url):
    """Function confirm that web page is accessible."""
    code = get_response_code(request_url)
    if code not in ACCESSIBLE_CODES:
        return False

    return True


def get_implanted_pattern(request_url):
    """Function confirm that web page is implanted."""

    try:
        headers = {
            'user-agent':
            'mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/115.0.0.0 safari/537.36'
        }
        path = '/webui/logoutconfirm.html'
        query = 'logon_hash=1'
        test_url = f"{request_url}{path}?{query}"
        print(test_url)
        # ignore verifying the ssl certificate
        response = requests.post(test_url,
                                 headers=headers,
                                 allow_redirects=False,
                                 verify=False,
                                 timeout=5)

        string = response.text.strip()
        if is_hexadecimal_string(string):
            return string

        return None
        #return is_hexadecimal_string(string)
    except Exception as e:
        print(e)
        return None

if __name__ == '__main__':

    path_to_csv = os.path.join(os.path.dirname(__file__), "..", "data",
                               "use_shodan_and_ipdn.csv")

    fields = pd.read_csv(path_to_csv).to_dict(orient='records')
    print(f"Records found: {len(fields)}")

    #label_keys = ['access_code', 'hex_str', 'timestamp']
    label_keys = ['access_code', 'timestamp']
    output = []
    for field in fields:
        DEFAULT_VALUE = None
        label = dict.fromkeys(label_keys, DEFAULT_VALUE)

        SCHEMA = 'http'
        if field['ssl'] is not None:
            SCHEMA = 'https'

        field['url'] = f"{SCHEMA}://{field['service']}"
        print(field['url'])

        label['timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        label['access_code'] = get_response_code(field['url'])
        #if label['access_code'] not in ACCESSIBLE_CODES:
        #    output.append(field | label)
        #    continue

        #label['hex_str'] = get_implanted_pattern(field['url'])
        output.append(field | label)

    df = pd.DataFrame(output)
    path_to_csv = os.path.join(os.path.dirname(__file__), "..", "data",
                               "use_cve_2023_20198.csv")
    df.to_csv(path_to_csv, index=False, encoding='utf-8-sig')
