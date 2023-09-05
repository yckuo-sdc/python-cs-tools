#!/usr/bin/python3 
from package.ip2gov_adapter import Ip2govAdapter 
import helper.basic_query as query
import helper.anonymous_bind as annoymous
import helper.function as func
import pandas as pd
import os

ip2gov = Ip2govAdapter()

search_filters = {
    'country': 'tw', 
    'org': "Government Service Network (GSN)",
    'all': 'ldap',
};

services = query.basic_query(search_filters)

output = []
for service in services:
    print(service['ip'], service['port'])
    label = annoymous.is_anonymous_binding(service['ip'], service['port'])
    print(label)
    gov_data = ip2gov.get_gov_data_by_ip(service['ip'])
    output.append(service | {'department': gov_data['DEP']} | {'label': label})

output_dict = func.arr_dict_to_flat_dict(output)
df = pd.DataFrame(output_dict)
path_to_csv = os.path.dirname(__file__) + "/data/anonymous_bind_scan.csv"
df.to_csv(path_to_csv, index=False)
