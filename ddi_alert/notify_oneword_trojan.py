"""Module detect ddi events and send alert mail."""
#!/usr/bin/python3
import os
import sys

import pandas as pd
from elasticsearch_dsl import Q, Search

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import helper.function as func
import helper.network_validator as network
import webshell_detection_model as wdm
from mail.send_mail import SendMail
from package.elasticsearch_dsl_adapter import ElasticsearchDslAdapter
from package.ip2gov_adapter import Ip2govAdapter

mail = SendMail()
mail.set_recipient("t910729@gmail.com")
es = ElasticsearchDslAdapter()
ip2gov = Ip2govAdapter()

EARLY_STOPPING = True
GTE = "now-1h"
LT = "now"

network_directions = [
    {
        'rulename': 'request',
        'service_ip': 'dst',
        'service_port': 'dpt'
    },
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

        ip_field_name = f"{network_direction['service_ip']}.keyword"
        port_field_name = f"{network_direction['service_port']}.keyword"
        s.aggs.bucket('per_service_ips', 'terms', field=ip_field_name) \
            .bucket('service_ports_per_service_ip', 'terms', field=port_field_name)
        s = s[0:10]

        response = s.execute()

        print(s.to_dict())
        print(f"Total Hits: {response.hits.total}")

        print('Discovery Scannable Government Services...')
        scannable_services = []
        for service_ip in response.aggregations.per_service_ips.buckets:
            if not ip2gov.is_gov(service_ip.key):
                continue

            for service_port in service_ip.service_ports_per_service_ip.buckets:
                if not network.is_opened(service_ip.key, int(
                        service_port.key)):
                    continue

                service = {'ip': service_ip.key, 'port': service_port.key}
                scannable_services.append(service)
                print(f"service({service['ip']}:{service['port']}) is found")

        print('Detect Webshells per Service...')

        for service in scannable_services:

            if network_direction['rulename'] == 'request':
                q_per_service = q & Q("match", dst=service['ip']) & Q(
                    "match", dpt=service['port'])
            elif network_direction['rulename'] == 'response':
                q_per_service = q & Q("match", src=service['ip']) & Q(
                    "match", spt=service['port'])

            s = Search(using=es.get_es_node(), index='new_ddi*') \
                .query(q_per_service) \
                .filter("range", **{'@timestamp':{"gte": GTE, "lt": LT}}) \
                .sort({"@timestamp": {"order": "desc"}})

            s = s[0:10]
            response = s.execute()

            print(s.to_dict())
            print(f"Total Hits: {response.hits.total}")
            print(f"Total Process Hits: {len(response.hits.hits)}")

            selected_keys = [
                '@timestamp', 'ruleName', 'reason', 'request', 'cs8', 'fname',
                'fileHash', 'cs4', 'requestClientApplication', 'src', 'dst',
                'spt', 'dpt'
            ]

            filtered_source_data = func.filter_hits_by_keys(
                response.hits.hits, selected_keys)

            inputs = func.arr_dict_to_flat_dict(filtered_source_data)
            labels = wdm.get_webshell_labels(filtered_source_data,
                                             early_stopping=EARLY_STOPPING)
            results = inputs | labels
            df = pd.DataFrame(results)
            frames.append(df)

try:
    total_df = pd.concat(frames, ignore_index=True)
    print(total_df)
except Exception as e:
    print(e)

if total_df.empty:
    sys.exit('DataFrame is empty!')

interested_id = []
for index, row in total_df.iterrows():
    column_http_success = row['http_success']

    if column_http_success:
        interested_id.append(index)

if not interested_id:
    sys.exit('No Interested Events')

total_df = total_df.loc[interested_id]

# Enrich ip with organiztaion name
total_df['src'] = total_df['src'].apply(
    lambda x: f"{x} {ip2gov.get_gov_data_by_ip(x, 'ACC')}")
total_df['dst'] = total_df['dst'].apply(
    lambda x: f"{x} {ip2gov.get_gov_data_by_ip(x, 'ACC')}")

SUBJECT = "DDI Alert: Oneword Trojan"
table = total_df.to_html(justify='left', index=False)

mail.set_subject(SUBJECT)
mail.set_template_body(mapping=table)
mail.send()
