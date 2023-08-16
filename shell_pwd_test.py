#!/usr/bin/python3 
from package.elasticsearch_dsl_adapter import ElasticsearchDslAdapter 
from elasticsearch_dsl import Search
from elasticsearch_dsl import Q
import helper.function as func
from datetime import datetime
import pandas as pd
import numpy as np
import re

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
    .sort({"@timestamp": {"order": "desc"}})    

s = s[0:1000]

response = s.execute()

print(s.to_dict())
print('total hits: {}'.format(response.hits.total)) 


selected_keys = ['@timestamp', 'ruleName', 'cs8', 'fileHash'] 

filtered_source_data = func.filter_hits_by_keys(response.hits.hits, selected_keys)
 
keywords = []
for doc in filtered_source_data:
    keyword = None
    if doc['cs8']:
        pattern = '^\w*?(?=%3D)'
        result = re.search(pattern, doc['cs8'])
        if result:
            keyword = result.group() 

    keywords.append(keyword)
    

# Get unique values from a list
keywords = list(set(keywords))
    
print(keywords)
