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

network_directions = [
    #{
    #    'rulename': 'request',
    #    'service_ip': 'dst',
    #    'service_port': 'dpt'
    #},
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

EARLY_STOPPING = False
GTE = "now-1h"
LT = "now"

frames = []
for network_direction in network_directions:
    for target_shell in shell_categories:
        q = Q("match", ruleName=target_shell) & Q(
            "match", ruleName=network_direction['rulename']) & Q("match",
                                                                 app='HTTP')

        s = Search(using=es.get_es_node(), index='new_ddi_2023.*') \
            .query(q) \
            .filter("range", **{'@timestamp':{"gte": GTE,"lt": LT}}) \
            .sort({"@timestamp": {"order": "desc"}})

        s = s[0:10]

        response = s.execute()

        print(s.to_dict())
        print(f"Total Hits: {response.hits.total}")

        selected_keys = [
            '@timestamp', 'ruleName', 'reason', 'Serverity', 'request', 'cs8',
            'fileHash', 'cs4', 'requestClientApplication', 'src', 'dst', 'spt',
            'dpt'
        ]

        filtered_source_data = func.filter_scan_hits_by_keys(
            s.scan(), selected_keys)

        inputs = func.arr_dict_to_flat_dict(filtered_source_data)
        df = pd.DataFrame(inputs)

        print(df)
        frames.append(df)

try:
    total_df = pd.concat(frames)
    print(total_df)
except Exception as e:
    print(e)

if total_df.empty:
    sys.exit('DataFrame is empty!')

dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
subject = f"webshell alert on {dt}"
table = total_df.to_html(justify='left', index=False)

mail.set_subject(subject)
mail.set_template_body(mapping=table)
mail.send()
