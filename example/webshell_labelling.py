#!/usr/bin/python3 
import json
import re
from datetime import datetime

import pandas as pd

import helper.http_validator as http
from package.elasticsearch_adapter import ElasticsearchAdapter
from package.ip2org_adapter import Ip2orgAdapter
from package.network_utility import NetworkUtility
from package.virustotal import VirusTotal


def is_manipulated(useragent):
  pattern = '\([^)]+\)|\S+\/'
  result = re.findall(pattern, useragent)
  useragent_count = len(result)
  print('{}: {}'.format(useragent, useragent_count))
  if useragent_count <= 5:
    return True
  return False
  

es = ElasticsearchAdapter()
vt = VirusTotal()
ip2org = Ip2orgAdapter()

indices = 'new_ddi*'

# define the query
query = {    
  "from": 0,
  "size": 0,
  "query": {
    "bool": {
      "must": [
        { "exists": { "field": "request" }},
        { "match": { "app": "HTTP" }},
        { "match": { "ruleName": "Response" }},
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
      ]
      #],
      #"filter": [
      #  { "range": { "@timestamp": { "gte": "now-7d/d", "lte": "now/d" }}}
      #]
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
          },
          "aggs": {
            "service_ips":{
              "terms": {
                "field": "src.keyword"
              }
            }
          }
        }
      }
    }
  }
}

data = es.aggregate_documents(indices, query, 'requests')
request_buckets = data['buckets']
print('Total buckets: {}'.format(data['total']))

request_list = list()
rulename_response_list = list()
rulename_request_list = list()
service_ip_list = list()
is_org_list = list()
reachable_list = list()
success_list = list()
malicious_list = list()
manipulated_list = list()
    
for index, request_bucket in enumerate(request_buckets):

    rulename_buckets = request_bucket['rulenames']['buckets']

    service_ips_in_request = list()
    for rulename_index, rulename_bucket in enumerate(rulename_buckets):
        service_ip_buckets = rulename_bucket['service_ips']['buckets']
        service_ips_in_rulename = ' '.join(str(value['key']) for service_ip_index, value in enumerate(service_ip_buckets))
        service_ips_in_request.append(service_ips_in_rulename)

    rulename = ' '.join(str(value['key']) for rulename_id, value in enumerate(rulename_buckets))
    service_ip = ' '.join(service_ips_in_request) 

    request = request_bucket['key']
    is_org, reachable, success, malicious = False, False, False, False

    net_utl = NetworkUtility(request)

    #if net_utl.get_ip(): 
    #   ip = net_utl.get_ip()
    #else:
    #   ip = service_ip

    netloc = net_utl.get_netloc() 
    is_org = ip2org.is_org(service_ip)

    if is_org:
        reachable = net_utl.is_reachable()
        if reachable:
            success = http.is_successful(request)
            if success:
                malicious = vt.is_malicious(netloc)

    print('{}. request: {}, is_org: {},  reachable: {}, success: {}, malicious: {}'.format(index+1, request, int(is_org), int(reachable), int(success), int(malicious)))

    request_list.append(request)
    rulename_response_list.append(rulename)
    service_ip_list.append(service_ip)
    is_org_list.append(int(is_org))
    reachable_list.append(int(reachable))
    success_list.append(int(success))
    malicious_list.append(int(malicious))


# request validation
for request in request_list:
    manipulated = False
    query = {    
      "from": 0,
      "size": 0,
      "query": {
        "bool": {
          "must": [
            {"match": {"ruleName": "REQUEST" }},
            {"match": {"request": request }}
          ]
        }
      },
      "aggs": {
        "useragents": {
          "terms": {
            "field": "requestclientapplication.keyword"
          },
          "aggs": {
            "rulenames": {
                "terms": {
                    "field": "ruleName.keyword"
                }
            }
          }
        }
      }
    }

    data = es.aggregate_documents(indices, query, 'useragents')
    useragent_buckets = data['buckets']
    rulenames_in_request = list()

    for useragent_index, useragent_bucket in enumerate(useragent_buckets):
        rulename_buckets = useragent_bucket['rulenames']['buckets']
        rulenames_in_useragent = ' '.join(str(value['key']) for rulename_index, value in enumerate(rulename_buckets))
        rulenames_in_request.append(rulenames_in_useragent)

        useragent = useragent_bucket['key']
        if is_manipulated(useragent):
            manipulated = True


    manipulated_list.append(int(manipulated))
    rulename = ' '.join(rulenames_in_request) 
    rulename_request_list.append(rulename)

# Export to csv
current_datetime = datetime.now().strftime("%Y_%m_%d_%I_%M_%S")
path = 'data/soar_' + current_datetime + '.csv'

csv_dict = {
    'request': request_list,
    'rulename_response': rulename_response_list,
    'rulename_request': rulename_request_list,
    'service_ip': service_ip_list,
    'is_org': is_org_list,
    'reachable': reachable_list,
    'success': success_list,
    'malicious': malicious_list,
    'manipulated': manipulated_list
}

#print(csv_dict)

df = pd.DataFrame(csv_dict)
df.to_csv(path, index=False)
