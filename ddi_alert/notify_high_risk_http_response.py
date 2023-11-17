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
#pylint: enable=wrong-import-position

mail = SendMail()
mail.set_ddi_alert_recipients()
es = ElasticsearchDslAdapter()
ip2gov = Ip2govAdapter()
dp = DDIProcessor()

GTE = "now-1h"
LT = "now"

SEVERITY = "8"

print("Search high risk http response...")
q = Q("match", Serverity=SEVERITY) & Q("match", app='HTTP') & Q(
    "match", ruleName='response')

s = Search(using=es.get_es_node(), index='new_ddi*') \
    .query(q) \
    .filter("range", **{'@timestamp':{"gte": GTE,"lt": LT}}) \
    .sort({"@timestamp": {"order": "desc"}})

s = s[0:10]
response = s.execute()

print(s.to_dict())
print(f"Total Hits: {response.hits.total}")

high_severities = dp.filter_all_hits_by_selected_fields(s.scan())

df = pd.DataFrame(high_severities)
print(df)

if df.empty:
    print('DataFrame is empty!')
    sys.exit(0)

# Enrich ip with organization name
df['src'] = df['src'].apply(
    lambda x: f"{x} {ip2gov.get(x, 'ACC')}")
df['dst'] = df['dst'].apply(
    lambda x: f"{x} {ip2gov.get(x, 'ACC')}")

SUBJECT = "DDI Alert: High Risk Http Response"
TABLE = df.to_html(justify='left', index=False)

mail.set_subject(SUBJECT)
mail.set_template_body(mapping=TABLE)
mail.send()
