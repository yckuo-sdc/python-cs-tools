#!/usr/bin/python3 
import json
import re
from datetime import datetime
from urllib.parse import unquote

import numpy as np
import pandas as pd
from elasticsearch_dsl import Q, Search

import helper.function as func
from package.elasticsearch_dsl_adapter import ElasticsearchDslAdapter

es = ElasticsearchDslAdapter()

shell_categories = [
    'chopper', # 0 
    'antsword', # 1
    'behinder', # 2
    'godzilla', # 3
]

target_shell_index = 3
target_shell = shell_categories[target_shell_index]

q = Q("match", ruleName=target_shell) & Q("match", app='HTTP')

s = Search(using=es.get_es_node(), index='new_ddi*') \
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
        keyword = unquote(doc['cs8'])
    #    pattern = '^\w*?(?=%3D)'
    #    result = re.search(pattern, doc['cs8'])
    #    if result:
    #        keyword = result.group() 

    keywords.append(keyword)
    

# Get unique values from a list
keywords = list(set(keywords))
    
print(json.dumps(keywords, indent=2))
