"""Module detect ddi events and send alert mail."""
#!/usr/bin/python3
import os
import sys

import pandas as pd
from elasticsearch_dsl import Q, Search

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from mail.send_mail import SendMail
from package.ddi_processor import DDIProcessor
from package.elasticsearch_dsl_adapter import ElasticsearchDslAdapter
from package.ip2gov_adapter import Ip2govAdapter

mail = SendMail()
mail.set_ddi_alert_recipients()
es = ElasticsearchDslAdapter()
ip2gov = Ip2govAdapter()
dp = DDIProcessor()

GTE = "now-1h"
LT = "now"

useragents = [
    "curl",
    "certutil",
    "wget",
    "python",
]

USERAGENT_STR = ' '.join(useragents)

print("Search useragents with filehash...")
q = Q('bool',
      must=[Q('exists', field='fileHash')],
      should=[
          Q("match", requestClientApplication=USERAGENT_STR),
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

print("Search useragents without filehash...")
useragents_with_filehash = dp.filter_all_hits_by_selected_fields(s.scan())

q = Q("match", requestClientApplication='certutil')

s = Search(using=es.get_es_node(), index='new_ddi*') \
    .query(q) \
    .filter("range", **{'@timestamp':{"gte": GTE,"lt": LT}}) \
    .sort({"@timestamp": {"order": "desc"}})

s = s[0:10]
response = s.execute()

print(s.to_dict())
print(f"Total Hits: {response.hits.total}")

useragents_without_filehash = dp.filter_all_hits_by_selected_fields(s.scan())

df = pd.concat([
    pd.DataFrame(useragents_with_filehash),
    pd.DataFrame(useragents_without_filehash)
],
               ignore_index=True)
print(df)

if df.empty:
    print('DataFrame is empty!')
    sys.exit(0)

# Enrich ip with organiztaion name
df['src'] = df['src'].apply(lambda x: f"{x} {ip2gov.get(x, 'ACC')}")
df['dst'] = df['dst'].apply(lambda x: f"{x} {ip2gov.get(x, 'ACC')}")

SUBJECT = "DDI Alert: Bot Useragent"
TABLE = df.to_html(justify='left', index=False)

mail.set_subject(SUBJECT)
mail.set_template_body(mapping=TABLE)
mail.send()
