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
mail.set_predefined_recipient("ddi_alert")
es = ElasticsearchDslAdapter()
dp = DDIProcessor()

GTE = "now-1h"
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

if df.empty:
    print('DataFrame is empty!')
    sys.exit(0)

df = dp.enrich_dataframe(df)
print(df)

SUBJECT = "DDI Alert: Hack Tool"
TABLE = df.to_html(justify='left', index=False)

mail.set_subject(SUBJECT)
mail.set_template_body(mapping=TABLE)
mail.send()
