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

    is_ping_successful = ip2gov.ping()
    if is_ping_successful:
        print('ip2gov: Yay Connected')
    else:
        print('ip2gov: Awww it could not connect!')

    search_filters = [
        {
            'asn': 'AS4782',
            'ssl.cert.issuer.CN': 'Kubernetes Ingress Controller Fake Certificate'
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

        if is_ping_successful:
            data = ip2gov.get(field['ip'])
            label['dep'] = data.get('DEP')
            label['class'] = data.get('Class')
            label['acc'] = data.get('ACC')

        output.append(field | label)

    df = pd.DataFrame(output)
    # Keep first duplicate value
    df = df.drop_duplicates(subset=['service'])

    path_to_csv = os.path.join(os.path.dirname(__file__), "..", "data",
                               "use_shodan_and_ipdn.csv")
    df.to_csv(path_to_csv, index=False, encoding='utf-8-sig')
