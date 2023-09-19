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

mail = SendMail()
mail.set_recipient("t910729@gmail.com")
es = ElasticsearchDslAdapter()
ip2gov = Ip2govAdapter()

GTE = "now-1h"
LT = "now"

q = Q("match", requestClientApplication="curl")
s = Search(using=es.get_es_node(), index='new_ddi_2023.*') \
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

filtered_source_data = func.filter_hits_by_keys(response.hits.hits,
                                                selected_keys)

inputs = func.arr_dict_to_flat_dict(filtered_source_data)
results = inputs
total_df = pd.DataFrame(results)
print(total_df)

if total_df.empty:
    print('DataFrame is empty!')
    sys.exit(0)

dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
subject = f"curl alert on {dt}"
table = total_df.to_html(justify='left', index=False)

mail.set_subject(subject)
mail.set_template_body(mapping=table)
mail.send()
