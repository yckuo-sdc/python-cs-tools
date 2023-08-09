#!/usr/bin/python3 
from package.elasticsearch_adapter import ElasticsearchAdapter 
from package.ip2org_adapter import Ip2orgAdapter 
from package.virustotal import VirusTotal
from package.network_utility import NetworkUtility
from datetime import datetime
import helper.http_validator as http
import pandas as pd
import json
import re

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

indices = 'new_ddi_2023.*'

# define the query
query = {    
  "from": 0,
  "size": 0,
  "query": {
    "bool": {
      "must": [
        { "exists": { "field": "request" }},
        { "match": { "app": "HTTP" }},
        { "bool": {
          "should": [
            { "match": { "ruleName": "Response" }},
            { "match": { "ruleName": "RESPONSE" }},
            { "match": { "ruleName": "response" }}
          ]
        }},
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
      "filter": [
        { "range": { "@timestamp": { "gte": "now-7d/d", "lte": "now/d" }}}
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

url_list = list()
rulename_list = list()
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

    url = request_bucket['key']
    is_org, reachable, success, malicious = False, False, False, False

    net_utl = NetworkUtility(url)

    #if net_utl.get_ip(): 
    #   ip = net_utl.get_ip()
    #else:
    #   ip = service_ip

    netloc = net_utl.get_netloc() 
    is_org = ip2org.is_org(service_ip)

    if is_org:
        reachable = net_utl.is_reachable()
        if reachable:
            success = http.is_successful(url)
            if success:
                malicious = vt.is_malicious(netloc)

    print('{}. url: {}, is_org: {},  reachable: {}, success: {}, malicious: {}'.format(index+1, url, int(is_org), int(reachable), int(success), int(malicious)))

    url_list.append(url)
    rulename_list.append(rulename)
    service_ip_list.append(service_ip)
    is_org_list.append(int(is_org))
    reachable_list.append(int(reachable))
    success_list.append(int(success))
    malicious_list.append(int(malicious))


# request validation
for url in url_list:
    manipulated = False
    query = {    
      "from": 0,
      "size": 0,
      "query": {
        "bool": {
          "must": [
            {"match": {"ruleName": "REQUEST"}},
            {"match": {"request": url}}
          ]
        }
      },
      "aggs": {
        "useragents": {
          "terms": {
            "field": "requestClientApplication.keyword"
          }
        }
      }
    }

    data = es.aggregate_documents(indices, query, 'useragents')
    useragent_buckets = data['buckets']
    #print('Total buckets: {}'.format(data['total']))
    for index, useragent_bucket in enumerate(useragent_buckets):
        useragent = useragent_bucket['key']
        if is_manipulated(useragent):
            manipulated = True
            break
    manipulated_list.append(int(manipulated))

# Export to csv
current_datetime = datetime.now().strftime("%Y_%m_%d_%I_%M_%S")
path = 'data/soar_' + current_datetime + '.csv'

csv_dict = {
    'url': url_list,
    'rulename': rulename_list,
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
