#!/usr/bin/python3 
from package.elasticsearch_dsl_adapter import ElasticsearchDslAdapter 
from elasticsearch_dsl import Search
from elasticsearch_dsl import Q
from package.network_utility import NetworkUtility
from datetime import datetime
import helper.network_validator as network
import helper.function as func
import webshell_detection_model as wdm 
import pandas as pd
import numpy as np
import os

es = ElasticsearchDslAdapter()

shell_categories = [
    'chopper', # 0 
    'antsword', # 1
    'behinder', # 2
    'godzilla', # 3
]

target_shell_index = 0
target_shell = shell_categories[target_shell_index]

q = Q("match", ruleName=target_shell) & Q("match", app='HTTP')

s = Search(using=es.get_es_node(), index='new_ddi_2023.*') \
    .query(q) \
    .filter("range", **{'@timestamp':{"gte": "now-14d/d","lt": "now/d"}}) \
    .sort({"@timestamp": {"order": "desc"}})    

s.aggs.bucket('per_dsts', 'terms', field='dst.keyword') \
    .bucket('dpts_per_dst', 'terms', field='dpt.keyword')
s = s[0:5]

response = s.execute()

print(s.to_dict())
print('Total Hits: {}'.format(response.hits.total)) 

print('Discovery Scannable Services')
scannable_services = []
for dst in response.aggregations.per_dsts.buckets:
    for dpt in dst.dpts_per_dst.buckets:
        if network.is_opened(dst.key, int(dpt.key)):
            service = {'ip': dst.key, 'port': dpt.key} 
            scannable_services.append(service)

print('Detect Webshells per Service')
frames = [] 
for service in scannable_services:  
    q_per_service = q & Q("match", dst=service['ip']) & Q("match", dpt=service['port'])

    s = Search(using=es.get_es_node(), index='new_ddi_2023.*') \
        .query(q_per_service) \
        .filter("range", **{'@timestamp':{"gte": "now-21d/d","lt": "now/d"}}) \
        .sort({"@timestamp": {"order": "desc"}})    

    s = s[0:5]
    response = s.execute()

    print(s.to_dict())
    print('Total Hits: {}'.format(response.hits.total)) 
    print('Total Process Hits: {}'.format(len(response.hits.hits))) 

    selected_keys = ['@timestamp', 'ruleName', 'reason', 'request', 'cs8', 'fileHash', 'cs4', 'requestClientApplication', 'src', 'dst', 'spt', 'dpt'] 

    filtered_source_data = func.filter_hits_by_keys(response.hits.hits, selected_keys)

    inputs = func.arr_dict_to_flat_dict(filtered_source_data)
    labels = wdm.get_webshell_labels(filtered_source_data, early_stopping=False)
    results = inputs | labels 
    df = pd.DataFrame(results)
    frames.append(df)

try:
    total_df = pd.concat(frames)
    print(total_df)
except Exception as e:
    print(e)
    os._exit(0)

# Export to csv
current_datetime = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
path = 'data/' + target_shell + '_' + current_datetime + '.csv'
total_df.to_csv(path, index=False)

