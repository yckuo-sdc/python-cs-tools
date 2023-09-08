"""Module dicovery anonymous bind allowd hosts."""
#!/usr/bin/python3
import os

import pandas as pd

import helper.anonymous_bind as annoymous
import helper.basic_query as query
import helper.function as func
from package.ip2gov_adapter import Ip2govAdapter

ip2gov = Ip2govAdapter()

search_filters = {
    'country': 'tw', 
    'org': "Government Service Network (GSN)",
    'all': 'ldap',
}

services = query.basic_query(search_filters)

output = []
for service in services:
    print(service['ip'], service['port'])
    LABEL = annoymous.is_anonymous_binding(service['ip'], service['port'])
    print(LABEL)
    gov_data = ip2gov.get_gov_data_by_ip(service['ip'])
    output.append(service | {'department': gov_data['DEP']} | {'label': LABEL})

output_dict = func.arr_dict_to_flat_dict(output)
df = pd.DataFrame(output_dict)
path_to_csv = os.path.dirname(__file__) + "/data/anonymous_bind_scan.csv"
df.to_csv(path_to_csv, index=False)
