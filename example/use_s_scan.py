"""Module detect webshell and send alert mail."""
#!/usr/bin/python3
import sys
from datetime import datetime

import pandas as pd
from elasticsearch_dsl import Q, Search

import helper.function as func
from mail.send_mail import SendMail
from package.elasticsearch_dsl_adapter import ElasticsearchDslAdapter
from package.ip2gov_adapter import Ip2govAdapter

es = ElasticsearchDslAdapter()

GTE = "now-7d"
LT = "now"

q = Q('bool',
      should=[
          Q("match", requestClientApplication="curl"),
          Q("match", requestClientApplication="certutil")
      ],
      minimum_should_match=1)

s = Search(using=es.get_es_node(), index='new_ddi*') \
    .query(q) \
    .filter("range", **{'@timestamp':{"gte": GTE,"lt": LT}}) \
    .sort({"@timestamp": {"order": "desc"}})

s = s[0:10]
response = s.execute()

print(s.to_dict())
print(f"Total Hits: {response.hits.total}")

selected_keys = [
    '@timestamp', 'ruleName', 'reason', 'request', 'cs8', 'fileHash', 'cs4',
    'requestClientApplication', 'src', 'dst', 'spt', 'dpt'
]

filtered_source_data = func.filter_scan_hits_by_keys(s.scan(),
                                                selected_keys)

inputs = func.arr_dict_to_flat_dict(filtered_source_data)
results = inputs
total_df = pd.DataFrame(results)
print(total_df)

if total_df.empty:
    print('DataFrame is empty!')
    sys.exit(0)
