"""Module detect ddi events and send alert mail."""
#!/usr/bin/python3
import os
import sys

import pandas as pd
from elasticsearch_dsl import Q, Search

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import helper.function as func
from mail.send_mail import SendMail
from package.elasticsearch_dsl_adapter import ElasticsearchDslAdapter
from package.ip2gov_adapter import Ip2govAdapter

mail = SendMail()
mail.set_ddi_alert_recipients()
es = ElasticsearchDslAdapter()
ip2gov = Ip2govAdapter()

GTE = "now-1h"
LT = "now"

EVT_SUB_CAT = "Trojan"
HEURISTIC_FLAG = "0"  # Disable heuristic detection

selected_keys = [
    '@timestamp', 'ruleName', 'reason', 'Serverity', 'request', 'cs8', 'fname',
    'fileHash', 'cs4', 'requestClientApplication', 'src', 'dst', 'spt', 'dpt'
]

print("Search trojan http response...")
q = Q("match", evtSubCat=EVT_SUB_CAT) & Q("match", app='HTTP') & Q(
    "match", ruleName='response') & Q("match", cn7=HEURISTIC_FLAG)
s = Search(using=es.get_es_node(), index='new_ddi*') \
    .query(q) \
    .filter("range", **{'@timestamp':{"gte": GTE,"lt": LT}}) \
    .sort({"@timestamp": {"order": "desc"}})

s = s[0:10]
response = s.execute()

print(s.to_dict())
print(f"Total Hits: {response.hits.total}")

high_severities = func.filter_scan_hits_by_keys(s.scan(), selected_keys)

df = pd.DataFrame(high_severities)
print(df)

if df.empty:
    print('DataFrame is empty!')
    sys.exit(0)

# Enrich ip with organiztaion name
df['src'] = df['src'].apply(lambda x: f"{x} {ip2gov.get(x, 'ACC')}")
df['dst'] = df['dst'].apply(lambda x: f"{x} {ip2gov.get(x, 'ACC')}")

SUBJECT = "DDI Alert: Trojan Http Response"
TABLE = df.to_html(justify='left', index=False)

mail.set_subject(SUBJECT)
mail.set_template_body(mapping=TABLE)
mail.send()
