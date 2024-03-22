"""Module Proof of Concept Ricoh Service."""
import datetime
import os
import sys

import pandas as pd
import requests
from lxml import etree as ET

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

#pylint: disable=wrong-import-position
import helper.network_validator as network


#pylint: enable=wrong-import-position
def get_qnap_attrs(url):
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

        if response.status_code == 200:
            xml_content = response.content
            root = ET.fromstring(xml_content)

            displayModelNames = root.xpath('.//displayModelName')
            versions = root.xpath('.//version')

            return {
                    'displayModelName': displayModelNames[0].text,
                    'version': versions[0].text,
            }
        else:
            print("Failed to fetch XML content. Status code:",
                  response.status_code)
            return None

    except Exception as e:
        print(e)
        return None


if __name__ == '__main__':

    path_to_csv = os.path.join(os.path.dirname(__file__), "..", "data",
                               "zoomeye.csv")

    fields = pd.read_csv(path_to_csv).to_dict(orient='records')
    print(f"Records found: {len(fields)}")

    label_keys = ['poc_product', 'poc_os']
    output = []
    for field in fields:
        DEFAULT_VALUE = None
        label = dict.fromkeys(label_keys, DEFAULT_VALUE)
        url = field['url']
        qnap_attrs = get_qnap_attrs(url)

        if qnap_attrs:
            label['poc_product'] = qnap_attrs['displayModelName']
            label['poc_os'] =  qnap_attrs['version']
        print(url, qnap_attrs)
        #input()

        output.append(field | label)

    df = pd.DataFrame(output)
    path_to_csv = os.path.join(os.path.dirname(__file__), "..", "data",
                               "use_qnap.csv")
    df.to_csv(path_to_csv, index=False, encoding='utf-8-sig')
