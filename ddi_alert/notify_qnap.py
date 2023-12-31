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
from package.shodan_adapter import ShodanAdapter

#pylint: enable=wrong-import-position

mail = SendMail()
mail.set_predefined_recipient("ddi_alert")
es = ElasticsearchDslAdapter()
dp = DDIProcessor()
sa = ShodanAdapter()

GTE = "now-1h"
LT = "now"

search_filter = {
    'product': 'qnap',
    'asn': 'AS4782',
}

match_field = [{'label': 'ip', 'field': 'ip_str'}]

fields = sa.basic_query_cursor(search_filter, match_field)
qnap_ip_list = [f['ip'] for f in fields]

QNAP_IPS = ' '.join(qnap_ip_list)

print("Search qnaps...")
q = Q('bool',
      must=[Q("match", ruleName='response')],
      should=[Q("match", src=QNAP_IPS),
              Q("match", dst=QNAP_IPS)],
      minimum_should_match=1)

#q = Q("match", src=QNAP_IPS) | Q("match", dst=QNAP_IPS) & Q("match", ruleName='response')

s = Search(using=es.get_es_node(), index='new_ddi*') \
    .query(q) \
    .filter("range", **{'@timestamp':{"gte": GTE,"lt": LT}}) \
    .sort({"@timestamp": {"order": "desc"}})

s = s[0:10]
response = s.execute()

print(s.to_dict())
print(f"Total Hits: {response.hits.total}")

qnaps = dp.filter_all_hits_by_selected_fields(s.scan())

df = pd.DataFrame(qnaps)

if df.empty:
    print('DataFrame is empty!')
    sys.exit(0)

df = dp.enrich_dataframe(df)
print(df)

SUBJECT = "DDI Alert: QNAP"
TABLE = df.to_html(justify='left', index=False)

mail.set_subject(SUBJECT)
mail.set_template_body(mapping=TABLE)
mail.send()
