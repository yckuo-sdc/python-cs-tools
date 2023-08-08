#!/usr/bin/python3 
from package.elasticsearch_adapter import ElasticsearchAdapter 
from package.virustotal import VirusTotal
from datetime import datetime
import helper.network_validator as network
import helper.http_validator as http
import pandas as pd
import json
import csv
import os

es = ElasticsearchAdapter()
vt = VirusTotal()

path = 'data/soar_2023_08_04_05_15_44.csv'

df = pd.read_csv(path)
<<<<<<< HEAD
url_list = df['url'].values.tolist)


=======
url_list = df['url'].values.tolist()

print(url_list)
>>>>>>> d685d30d0b8feceef2997fa8f89bdaa4bcc24c4c



#indices = 'new_ddi_2023.*'
#
#
#
#
## define the query
#query = {    
#    'from': 0,
#    'size': 0,
#    'query': {
#        'bool': { 
#            'must': [ 
#                { "match": { "ruleName": "Response" }},
#			    { "exists": { "field": "request" }}
#             ],
#             "must_not": [
#                { "match": { "ruleName": "Email" }},
#                { "match": { "ruleName": "DNS" }}
#             ],
#             'filter': [ 
#                { 'range': { '@timestamp': { 'gte': 'now-7d/d', 'lte': 'now/d' }}}
#             ]
#        }
#    },
#    "aggs" : { 
#    	"requests" : { 
#    	  	"terms" : { 
#    			"field": "request.keyword"
#    	 	}
#      	}
#    }
#}
#
#data = es.aggregate_documents(indices, query)
#print('Total buckets: {}'.format(data['total']))
#
#url_list = list()
#reachable_list = list()
#success_list = list()
#malicious_list = list()
#    
#for index, bucket in enumerate(data['buckets']):
#
#    url = bucket['key']
#
#    reachable = False
#    success = False
#    malicious = False
#
#    reachable = network.is_reachable(url)
#    if reachable:
#        success = http.is_successful(url)
#        if success:
#            malicious = vt.is_malicious(url)
#
#    print('{}. url: {}, reachable: {}, success: {}, malicious: {}'.format(index+1, url, reachable, success, malicious))
#
#    url_list.append(url)
#    reachable_list.append(int(reachable))
#    success_list.append(int(success))
#    malicious_list.append(int(malicious))
#
## Export to csv
#current_datetime = datetime.now().strftime("%Y_%m_%d_%I_%M_%S")
#path = 'data/soar_' + current_datetime + '.csv'
#
#csv_dict = {
#    'url': url_list,
#    'reachable': reachable_list,
#    'success': success_list,
#    'malicious': malicious_list,
#}
#
#df = pd.DataFrame(csv_dict)
#df.to_csv(path, index=False)
