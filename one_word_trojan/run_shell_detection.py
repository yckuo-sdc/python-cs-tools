#!/usr/bin/python3
import os
import sys
from datetime import datetime

import numpy as np
import pandas as pd
from elasticsearch_dsl import Q, Search

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import helper.network_validator as network
from package.ddi_processor import DDIProcessor
from package.elasticsearch_dsl_adapter import ElasticsearchDslAdapter
from package.ip2gov_adapter import Ip2govAdapter

import webshell_detection_model as wdm

es = ElasticsearchDslAdapter()
ip2gov = Ip2govAdapter()
dp = DDIProcessor()

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

EARLY_STOPPING = True
gte = "now-14d/d"
lt = "now/d"

for network_direction in network_directions:
    for target_shell in shell_categories:
        q = Q("match", ruleName=target_shell) & Q(
            "match", ruleName=network_direction['rulename']) & Q("match",
                                                                 app='HTTP')

        s = Search(using=es.get_es_node(), index='new_ddi*') \
            .query(q) \
            .filter("range", **{'@timestamp':{"gte": gte,"lt": lt}}) \
            .sort({"@timestamp": {"order": "desc"}})

        s.aggs.bucket('per_service_ips', 'terms', field=network_direction['service_ip'] + '.keyword') \
            .bucket('service_ports_per_service_ip', 'terms', field=network_direction['service_port'] + '.keyword')
        s = s[0:5]

        response = s.execute()

        print(s.to_dict())
        print('Total Hits: {}'.format(response.hits.total))

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
                print('service({}:{}) is found'.format(service['ip'],
                                                       service['port']))

        print('Detect Webshells per Service...')
        frames = []
        for service in scannable_services:

            if network_direction['rulename'] == 'request':
                q_per_service = q & Q("match", dst=service['ip']) & Q(
                    "match", dpt=service['port'])
            elif network_direction['rulename'] == 'response':
                q_per_service = q & Q("match", src=service['ip']) & Q(
                    "match", spt=service['port'])

            s = Search(using=es.get_es_node(), index='new_ddi*') \
                .query(q_per_service) \
                .filter("range", **{'@timestamp':{"gte": gte, "lt": lt}}) \
                .sort({"@timestamp": {"order": "desc"}})

            s = s[0:5]
            response = s.execute()

            print(s.to_dict())
            print(f"Total Hits: {response.hits.total}")
            print(f"Total Process Hits: {len(response.hits.hits)}")

            inputs = dp.filter_all_hits_by_selected_fields(s.scan())
            labels = wdm.get_webshell_labels(inputs,
                                             early_stopping=EARLY_STOPPING)


            results = []
            for item1, item2 in zip(inputs, labels):
                results.append(item1 | item2)

            df = pd.DataFrame(results)
            frames.append(df)

        try:
            total_df = pd.concat(frames)
            print(total_df)
        except Exception as e:
            print(e)
            continue

        # Export to csv
        current_datetime = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

        path_to_csv = target_shell + '_' + network_direction[
            'rulename'] + '_' + current_datetime

        if not EARLY_STOPPING:
            path_to_csv = path_to_csv + '_no_early_stop'
        path_to_csv = path_to_csv + '.csv'

        path_to_csv = os.path.join(os.path.dirname(__file__), '..',
                                   'data/shell_trials', path_to_csv)

        if total_df.empty:
            print('DataFrame is empty!')
            continue

        total_df.to_csv(path_to_csv, index=False)
