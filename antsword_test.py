#!/usr/bin/python3 
from package.elasticsearch_dsl_adapter import ElasticsearchDslAdapter 
from elasticsearch_dsl import Search
from elasticsearch_dsl import Q
import webshell_detection_model as wdm 
import helper.function as func
from datetime import datetime
import pandas as pd
import numpy as np

es = ElasticsearchDslAdapter()

q = Q("match", ruleName='antsword') & Q("match", app='HTTP')

s = Search(using=es.get_es_node(), index='new_ddi_2023.*') \
    .query(q) \
    .filter("range", **{'@timestamp':{"gte": "now-14d/d","lt": "now/d"}}) \
    .sort({"@timestamp": {"order": "desc"}})    

s = s[0:5]

response = s.execute()

print(s.to_dict())
print('total hits: {}'.format(response.hits.total)) 


selected_keys = ['@timestamp', 'ruleName', 'request', 'cs8', 'fileHash', 'requestClientApplication', 'src', 'dst', 'spt', 'dpt'] 

filtered_source_data = func.filter_hits_by_keys(response.hits.hits, selected_keys)

inputs = func.arr_dict_to_flat_dict(filtered_source_data)

   
labels = wdm.get_webshell_labels(filtered_source_data)

results = inputs | labels 
for key, val in results.items():
    print (key, ":", val)

df = pd.DataFrame(results)

# Export to csv
current_datetime = datetime.now().strftime("%Y_%m_%d_%I_%M_%S")
path = 'data/antsword_' + current_datetime + '.csv'
df.to_csv(path, index=False)
