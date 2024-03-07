"""Module Proof of Concept Ricoh Service."""
import datetime
import os
import sys

import pandas as pd
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

#pylint: disable=wrong-import-position
import helper.network_validator as network

#pylint: enable=wrong-import-position
def get_response_code(url):
    try:
        headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        # ignore verifying the SSL certificate
        response = requests.get(url,
                                headers=headers,
                                allow_redirects=False,
                                verify=False,
                                timeout=5)
        return response.status_code
    except Exception as e:
        print(e)
        return None

if __name__ == '__main__':

    path_to_csv = os.path.join(os.path.dirname(__file__), "..", "data",
                               "geovision_shodan_censys_product_version.csv")

    fields = pd.read_csv(path_to_csv).to_dict(orient='records')
    print(f"Records found: {len(fields)}")

    label_keys = ['http_code']
    output = []
    for field in fields:
        DEFAULT_VALUE = None
        label = dict.fromkeys(label_keys, DEFAULT_VALUE)

        url = f"http://{field['service']}/UserSetting.cgi"
        label['http_code'] = get_response_code(url)
        print(url, label['http_code'])
        #input()

        output.append(field | label)

    df = pd.DataFrame(output)
    path_to_csv = os.path.join(os.path.dirname(__file__), "..", "data",
                               "use_geovision.csv")
    df.to_csv(path_to_csv, index=False, encoding='utf-8-sig')
