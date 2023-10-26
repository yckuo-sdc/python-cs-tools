"""Module Proof of Concept for CVE-2023-20198."""
import datetime
import os
import sys

import pandas as pd
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from package.ip2gov_adapter import Ip2govAdapter
from package.shodan_adapter import ShodanAdapter

if __name__ == '__main__':

    ip2gov = Ip2govAdapter()
    sa = ShodanAdapter()

    search_filters = [
        {
            'asn': 'AS4782',
            'http.title': 'NetScaler AAA',
        }, 
        {
            'country': 'tw',
            'http.title': 'NetScaler AAA',
        },
    ]


    match_field = [{
        'label': 'ip',
        'field': 'ip_str'
    }, {
        'label': 'port',
        'field': 'port'
    }, {
        'label': 'product',
        'field': 'product'
    }, {
        'label': 'ssl',
        'field': {
            'ssl': 'cipher'
        },
    }, {
        'label': 'module',
        'field': {
            '_shodan': 'module'
        },
    }]


    fields = []
    for search_filter in search_filters:
        field = sa.basic_query_cursor(search_filter, match_field)
        fields.extend(field)

    label_keys = ['dep', 'class', 'acc']
    output = []
    for field in fields:
        DEFAULT_VALUE = None
        label = dict.fromkeys(label_keys, DEFAULT_VALUE)

        field['service'] = f"{field['ip']}:{field['port']}"

        gov_data = ip2gov.get_gov_data_by_ip(field['ip'])
        if gov_data:
            label['dep'] = gov_data.get('DEP')
            label['class'] = gov_data.get('Class')
            label['acc'] = gov_data.get('ACC')

        output.append(field | label)

    df = pd.DataFrame(output)
    path_to_csv = os.path.join(os.path.dirname(__file__), "..", "data",
                               "use_shodan_and_ipdn.csv")
    df.to_csv(path_to_csv, index=False, encoding='utf-8-sig')
