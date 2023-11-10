"""Module detect ddi events and send alert mail."""
#!/usr/bin/python3
import os
import sys
from datetime import datetime

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

network_directions = [
    {
        'rulename': 'response',
        'service_ip': 'src',
        'service_port': 'spt'
    },
]

shell_categories = [
    'webshell',
    'possible_smchopperphpa',
    'chopper',
    'antsword',
    'behinder',
    'godzilla',
]

frames = []
for network_direction in network_directions:
    for target_shell in shell_categories:
        q = Q("match", ruleName=target_shell) & Q(
            "match", ruleName=network_direction['rulename']) & Q("match",
                                                                 app='HTTP')

        s = Search(using=es.get_es_node(), index='new_ddi*') \
            .query(q) \
            .filter("range", **{'@timestamp':{"gte": GTE,"lt": LT}}) \
            .sort({"@timestamp": {"order": "desc"}})

        s = s[0:10]

        response = s.execute()

        print(s.to_dict())
        print(f"Total Hits: {response.hits.total}")


        webshell_responses = dp.filter_all_hits_by_selected_fields(s.scan())
        df = pd.DataFrame(webshell_responses)

        print(df)
        frames.append(df)

total_df = pd.DataFrame()
try:
    total_df = pd.concat(frames, ignore_index=True)
    print(total_df)
except Exception as e:
    print(e)

if total_df.empty:
    sys.exit('DataFrame is empty!')

# Enrich ip with organiztaion name
total_df['src'] = total_df['src'].apply(
    lambda x: f"{x} {ip2gov.get(x, 'ACC')}")
total_df['dst'] = total_df['dst'].apply(
    lambda x: f"{x} {ip2gov.get(x, 'ACC')}")

SUBJECT = "DDI Alert: Webshell Response"
TABLE = total_df.to_html(justify='left', index=False)

mail.set_subject(SUBJECT)
mail.set_template_body(mapping=TABLE)
mail.send()
