#!/usr/bin/python3 
import helper.basic_query as query
import helper.anonymous_bind as annoymous
import helper.function as func
import pandas as pd

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
    output.append(service | {'label': label})

ouptu_dict = func.arr_dict_to_flat_dict(output)
df = pd.DataFrame(results)
path_to_csv = os.path.dirname(__file__) + "/data/anonymous_bind_scan.csv"
df.to_csv(path_to_csv, index=False)
