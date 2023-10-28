import json
from urllib.parse import urlparse

#from helper.http_validator import * 
import helper.http_validator as http
import helper.network_validator as network
from package.elasticsearch_adapter import ElasticsearchAdapter
from package.virustotal import VirusTotal

es = ElasticsearchAdapter()
vt = VirusTotal()

indices = 'new_ddi*'

# define the query
query = {    
    'from': 0,
    'size': 0,
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



#data = es.search_documents(indices, query)

#for doc in data['documents']:
#    url = doc['_source']['request']
#    vid = vt.scan_url(url)
#    stats = vt.get_scan_report(vid)
#    print('url: {}'.format(url))
#    print('stats: {}'.format(stats))


data = es.aggregate_documents(indices, query)
print('Total buckets: {}'.format(data['total']))
    
for index, bucket in enumerate(data['buckets']):

    url = bucket['key']
    url_obj = urlparse(url)
    hostname = url_obj.hostname
    if url_obj.port is None and url_obj.scheme == 'http':
        port = 80

    opened=  network.is_opened(hostname, port)
    success = http.is_successful(url)
    malicious = vt.is_malicious(url)

    print('{}. url: {}, opened: {}, successfull: {}, malicious: {}'.format(index+1, url, opened, success, malicious))
