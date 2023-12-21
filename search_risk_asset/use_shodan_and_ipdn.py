"""Module Proof of Concept for CVE-2023-20198."""
import os
import sys

import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

#pylint: disable=wrong-import-position
from package.ip2gov_adapter import Ip2govAdapter
from package.shodan_adapter import ShodanAdapter

#pylint: enable=wrong-import-position

if __name__ == '__main__':

    ip2gov = Ip2govAdapter()
    sa = ShodanAdapter()

    IS_PING_SUCCESSFUL = ip2gov.ping()
    if IS_PING_SUCCESSFUL:
        print('ip2gov: Yay Connected')
    else:
        print('ip2gov: Awww it could not connect!')

    search_filters = [
        {
            'all_no_quotes': 'RICOH',
            'asn': 'AS4782'
        },
        #{
        #    'port': '515,631,9100',
        #    'asn': 'AS4782'
        #},
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
        'label': 'os',
        'field': 'os'
    }, {
        'label': 'module',
        'field': {
            '_shodan': 'module'
        },
    }, {
        'label': 'tags',
        'field': 'tags'
    }]

    fields = []
    for search_filter in search_filters:
        field = sa.basic_query_cursor(search_filter, match_field)
        fields.extend(field)

    output = []
    for field in fields:
        field['service'] = f"{field['ip']}:{field['port']}"

        if IS_PING_SUCCESSFUL:
            label = ip2gov.get(field['ip'])
            output.append(field | label)
        else:
            output.append(field)

    df = pd.DataFrame(output)
    # Keep first duplicate value
    df = df.drop_duplicates(subset=['service'])
    df = df.sort_values(by='service')

    path_to_csv = os.path.join(os.path.dirname(__file__), "..", "data",
                               "use_shodan_and_ipdn.csv")
    df.to_csv(path_to_csv, index=False, encoding='utf-8-sig')
