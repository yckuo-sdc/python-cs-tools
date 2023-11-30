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

#pylint: enable=wrong-import-position

mail = SendMail()
mail.set_ddi_alert_recipients()
es = ElasticsearchDslAdapter()
dp = DDIProcessor()

GTE = "now-1h"
LT = "now"

FILE_TRANSFER_KEYWORD = "*File Transfer"

print("Search file transfer...")
q = Q("wildcard", ruleName__keyword=FILE_TRANSFER_KEYWORD)
s = Search(using=es.get_es_node(), index='new_ddi*') \
    .query(q) \
    .filter("range", **{'@timestamp':{"gte": GTE,"lt": LT}}) \
    .sort({"@timestamp": {"order": "desc"}})

s = s[0:10]
response = s.execute()

print(s.to_dict())
print(f"Total Hits: {response.hits.total}")

trojans = dp.filter_all_hits_by_selected_fields(s.scan())
df = pd.DataFrame(trojans)

if df.empty:
    print('DataFrame is empty!')
    sys.exit(0)

df = dp.enrich_dataframe(df)
print(df)

SUBJECT = "DDI Alert: File Transfer"
TABLE = df.to_html(justify='left', index=False)

mail.set_subject(SUBJECT)
mail.set_template_body(mapping=TABLE)
mail.send()
