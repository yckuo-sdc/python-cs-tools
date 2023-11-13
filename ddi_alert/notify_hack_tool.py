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

GTE = "now-1d"
LT = "now"

######## HKTL_PASS.COE, HKTL_PASSVIEW, HKTL_PDFRestrictionsRemover, HKTL_PRODKEY
##E.G.## HKTL_FILEUP, HKTL_KEYGEN, HKTL_CCDOOR
######## HKTL_PROXY, HKTL_RADMIN.component', HKTL_ETHERFLOOD
HACK_TOOL_KEYWORD = "HKTL*"

print("Search hack tool...")
q = Q("wildcard", ruleName__keyword=HACK_TOOL_KEYWORD)

s = Search(using=es.get_es_node(), index='new_ddi*') \
    .query(q) \
    .filter("range", **{'@timestamp':{"gte": GTE,"lt": LT}}) \
    .sort({"@timestamp": {"order": "desc"}})

s = s[0:10]
response = s.execute()

print(s.to_dict())
print(f"Total Hits: {response.hits.total}")

hack_tool_response = dp.filter_all_hits_by_selected_fields(s.scan())

df = pd.DataFrame(hack_tool_response)
print(df)

if df.empty:
    print('DataFrame is empty!')
    sys.exit(0)

# Enrich ip with organiztaion name
df['src'] = df['src'].apply(lambda x: f"{x} {ip2gov.get(x, 'ACC')}")
df['dst'] = df['dst'].apply(lambda x: f"{x} {ip2gov.get(x, 'ACC')}")

SUBJECT = "DDI Alert: Hack Tool"
TABLE = df.to_html(justify='left', index=False)

mail.set_subject(SUBJECT)
mail.set_template_body(mapping=TABLE)
mail.send()
