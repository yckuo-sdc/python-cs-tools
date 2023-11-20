"""Module detect ddi events and send alert mail."""
#!/usr/bin/python3
import os
import sys

import pandas as pd
from elasticsearch_dsl import Q, Search

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

#pylint: disable=wrong-import-position
from mail.send_mail import SendMail
from package.ddi_processor import DDIProcessor
from package.elasticsearch_dsl_adapter import ElasticsearchDslAdapter
from package.ip2gov_adapter import Ip2govAdapter
from package.virustotal import VirusTotal

#pylint: enable=wrong-import-position

mail = SendMail()
mail.set_ddi_alert_recipients()
dp = DDIProcessor()
es = ElasticsearchDslAdapter()
ip2gov = Ip2govAdapter()
vt = VirusTotal()

GTE = "now-1h"
LT = "now"

print("Search miner request...")
q = Q("match", ruleName='miner') & Q("match", ruleName='request')
s = Search(using=es.get_es_node(), index='new_ddi*') \
    .query(q) \
    .filter("range", **{'@timestamp':{"gte": GTE,"lt": LT}}) \
    .sort({"@timestamp": {"order": "desc"}})

s = s[0:10]
response = s.execute()

print(s.to_dict())
print(f"Total Hits: {response.hits.total}")

dp.set_selected_fields([
    '@timestamp', 'ruleName', 'reason', 'Serverity', 'src', 'dst', 'spt', 'dpt'
])
miners = dp.filter_all_hits_by_selected_fields(s.scan())
selected_miner_indices = [
    i for i, m in enumerate(miners) if ip2gov.is_gov(m['src'])
]
selected_miners = [miners[i] for i in selected_miner_indices]
mine_ips = [m['dst'] for m in selected_miners]
labels = vt.get_malicious_number_by_ips(mine_ips)

results = []
for item1, item2 in zip(selected_miners, labels):
    results.append(item1 | item2)

df = pd.DataFrame(results)
print(df)

if df.empty:
    print('DataFrame is empty!')
    sys.exit(0)

interested_id = []
for index, row in df.iterrows():
    if row['vt_malicious_num']:
        interested_id.append(index)

if not interested_id:
    sys.exit('No VT Matches')

df = df.loc[interested_id]

# Enrich ip with organization name
df['src'] = df['src'].apply(lambda x: f"{x} {ip2gov.get(x, 'ACC')}")
df['dst'] = df['dst'].apply(lambda x: f"{x} {ip2gov.get(x, 'ACC')}")

SUBJECT = "DDI Alert: Miner Request"
TABLE = df.to_html(justify='left', index=False)

mail.set_subject(SUBJECT)
mail.set_template_body(mapping=TABLE)
mail.send()
