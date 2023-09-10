#!/usr/bin/python3
import glob
import os
from datetime import datetime
from io import StringIO
from pathlib import Path
from string import Template

import numpy as np
import pandas as pd
from elasticsearch_dsl import Q, Search
from premailer import transform

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

early_stopping = False
gte = "now-30m"
lt = "now"

for network_direction in network_directions:
    for target_shell in shell_categories:
        q = Q("match", ruleName=target_shell) & Q(
            "match", ruleName=network_direction['rulename']) & Q("match",
                                                                 app='HTTP')

        s = Search(using=es.get_es_node(), index='new_ddi_2023.*') \
            .query(q) \
            .filter("range", **{'@timestamp':{"gte": gte,"lt": lt}}) \
            .sort({"@timestamp": {"order": "desc"}})

        s.aggs.bucket('per_service_ips', 'terms', field=network_direction['service_ip'] + '.keyword') \
            .bucket('service_ports_per_service_ip', 'terms', field=network_direction['service_port'] + '.keyword')
        s = s[0:10]

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

            s = Search(using=es.get_es_node(), index='new_ddi_2023.*') \
                .query(q_per_service) \
                .filter("range", **{'@timestamp':{"gte": gte, "lt": lt}}) \
                .sort({"@timestamp": {"order": "desc"}})

            s = s[0:10]
            response = s.execute()

            print(s.to_dict())
            print('Total Hits: {}'.format(response.hits.total))
            print('Total Process Hits: {}'.format(len(response.hits.hits)))

            selected_keys = [
                '@timestamp', 'ruleName', 'reason', 'request', 'cs8',
                'fileHash', 'cs4', 'requestClientApplication', 'src', 'dst',
                'spt', 'dpt'
            ]

            filtered_source_data = func.filter_hits_by_keys(
                response.hits.hits, selected_keys)

            inputs = func.arr_dict_to_flat_dict(filtered_source_data)
            labels = wdm.get_webshell_labels(filtered_source_data,
                                             early_stopping=early_stopping)
            results = inputs | labels
            df = pd.DataFrame(results)
            frames.append(df)

        try:
            total_df = pd.concat(frames)
            print(total_df)
        except Exception as e:
            print(e)
            continue


        if total_df.empty:
            print('DataFrame is empty!')
            continue


        interested_id = []
        for index, row in total_df.iterrows():
            column_http_success = row['http_success']

            if column_http_success:
                interested_id.append(index)

        if not interested_id:
            print("No Interested Events")
            continue

        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = f"{target_shell} ({network_direction}) alert on {dt}"
        textStream = StringIO()

        table = total_df.loc[interested_id].to_html(justify='left', index=False)
        template = Template(Path(os.path.join( \
                os.path.dirname(__file__), 'mail/template', 'rwd_ddi.html')) \
                .read_text('utf-8'))
        body = transform(template.substitute({ "table": table }))

        mail.set_subject(subject)
        mail.set_body(body)
        mail.send()
