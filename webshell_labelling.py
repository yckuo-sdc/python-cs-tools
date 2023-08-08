#!/usr/bin/python3 
from package.elasticsearch_adapter import ElasticsearchAdapter 
<<<<<<< HEAD
from package.ip2org_adapter import Ip2orgAdapter 
=======
>>>>>>> d685d30d0b8feceef2997fa8f89bdaa4bcc24c4c
from package.virustotal import VirusTotal
from datetime import datetime
import helper.network_validator as network
import helper.http_validator as http
import pandas as pd
import json

es = ElasticsearchAdapter()
vt = VirusTotal()
<<<<<<< HEAD
ip2org = Ip2orgAdapter()
=======
>>>>>>> d685d30d0b8feceef2997fa8f89bdaa4bcc24c4c

indices = 'new_ddi_2023.*'

# define the query
<<<<<<< HEAD
#query = {    
#    'from': 0,
#    'size': 1,
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


# define the query
query = {    
  "from": 0,
  "size": 0,
  "query": {
    "bool": {
      "must": [
        { "match": { "ruleName": "Response" }},
        { "exists": { "field": "request" }},
        { "bool": {
            "should": [
                { "bool": {
                    "must":[
                        { "match": { "evtCat": "Callback" }},
                        { "match": { "evtSubCat": "Malware" }}
                     ]
                 }},
                 {"bool": {
                    "must":[
                        { "match": { "evtCat": "Malware" }},
                        { "match": { "evtSubCat": "Trojan" }}
                    ]
                 }},
                 {"bool": {
                    "must":[
                        { "match": { "evtCat": "Grayware" }},
                        { "match": { "evtSubCat": "Hack Tool" }}
                    ]
                }},
                {"bool": {
                    "must":[
                        { "match": { "evtCat": "Access" }},
                        { "match": { "evtSubCat": "Web Application" }}
                    ]
                }}
            ]
         }}
      ],
      "must_not": [
        {"match": {"ruleName": "DNS"}},
        {"match": {"ruleName": "Email"}}
      ]
    }
  },
  "aggs": {
    "requests": {
      "terms": {
        "field": "request.keyword"
      },
      "aggs": {
        "rulenames":{
          "terms": {
            "field": "ruleName.keyword"
          }
        }
      }
    }
  }
}


=======
query = {    
    'from': 0,
    'size': 1,
    'query': {
        'bool': { 
            'must': [ 
                { "match": { "ruleName": "Response" }},
			    { "exists": { "field": "request" }}
             ],
             "must_not": [
                { "match": { "ruleName": "Email" }},
                { "match": { "ruleName": "DNS" }}
             ],
             'filter': [ 
                { 'range': { '@timestamp': { 'gte': 'now-7d/d', 'lte': 'now/d' }}}
             ]
        }
    },
    "aggs" : { 
    	"requests" : { 
    	  	"terms" : { 
    			"field": "request.keyword"
    	 	}
      	}
    }
}

>>>>>>> d685d30d0b8feceef2997fa8f89bdaa4bcc24c4c
data = es.aggregate_documents(indices, query)
print('Total buckets: {}'.format(data['total']))

url_list = list()
<<<<<<< HEAD
is_org_list = list()
=======
>>>>>>> d685d30d0b8feceef2997fa8f89bdaa4bcc24c4c
reachable_list = list()
success_list = list()
malicious_list = list()
    
for index, bucket in enumerate(data['buckets']):

    url = bucket['key']
<<<<<<< HEAD
    
    is_org = False
=======

>>>>>>> d685d30d0b8feceef2997fa8f89bdaa4bcc24c4c
    reachable = False
    success = False
    malicious = False

<<<<<<< HEAD
    ip = network.get_ip_by_url(url)
    is_org = ip2org.is_org(ip)

    if is_org:
        reachable = network.is_reachable(url)
        if reachable:
            success = http.is_successful(url)
            if success:
                #malicious = vt.is_malicious(url)
                malicious = False

    print('{}. url: {}, is_org: {},  reachable: {}, success: {}, malicious: {}'.format(index+1, url, is_org, reachable, success, malicious))

    url_list.append(url)
    is_org_list.append(int(is_org))
=======
    reachable = network.is_reachable(url)
    if reachable:
        success = http.is_successful(url)
        if success:
            malicious = vt.is_malicious(url)

    print('{}. url: {}, reachable: {}, success: {}, malicious: {}'.format(index+1, url, reachable, success, malicious))

    url_list.append(url)
>>>>>>> d685d30d0b8feceef2997fa8f89bdaa4bcc24c4c
    reachable_list.append(int(reachable))
    success_list.append(int(success))
    malicious_list.append(int(malicious))

# Export to csv
current_datetime = datetime.now().strftime("%Y_%m_%d_%I_%M_%S")
path = 'data/soar_' + current_datetime + '.csv'

csv_dict = {
    'url': url_list,
    'reachable': reachable_list,
    'success': success_list,
    'malicious': malicious_list,
}

df = pd.DataFrame(csv_dict)
df.to_csv(path, index=False)
