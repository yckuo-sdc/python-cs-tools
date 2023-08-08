from dotenv import load_dotenv
from elasticsearch import Elasticsearch
import json
import os

class ElasticsearchAdapter:   

    def __init__(self,  host="", port=""): 
        if host == "" or port == "":
            load_dotenv()
<<<<<<< HEAD
            self.host = os.getenv("ES_HOST")
            self.port = os.getenv("ES_PORT")
=======
            self.host = os.getenv("DDI_ES_HOST")
            self.port = os.getenv("DDI_ES_PORT")
>>>>>>> d685d30d0b8feceef2997fa8f89bdaa4bcc24c4c
        else:
            self.host = host 
            self.port = port
            
        self.es = None
        self.es = Elasticsearch([{ 'host': self.host, 'port': self.port }])

        if self.es.ping():
            print('Yay Connected')
        else:
            print('Awww it could not connect!')
            os._exit(0) 

    def search_documents(self, index, query):
        data = {}
        try:
            result= self.es.search(index=index, body=query)
            #print(result)
        except Exception as e:
            print('Error in indexing data')
            print(str(e))
        finally:
            data['total'] = result['hits']['total'] 
            data['documents'] = result['hits']['hits']
            return data

    def aggregate_documents(self, index, query):
        data = {}
        try:
            result= self.es.search(index=index, body=query)
        except Exception as e:
            print('Error in indexing data')
            print(str(e))
        finally:
            #print(result)
            buckets = result['aggregations']['requests']['buckets']
            data['total'] = len(buckets)
            data['buckets'] = buckets
            return data 

if __name__ == '__main__':
    es = ElasticsearchAdapter()

    indices = 'new_ddi_2023.*'

    # define the search query
    query = {    
        'from': 0,
        'size': 10,
		'query': {
			'bool': { 
		    	'must': [ 
                    { "match": { "ruleName": "Response" }}
				 ],
				 "must_not": [
				 	{ "match": { "ruleName": "Email" }},
					{ "match": { "ruleName": "DNS" }}
				 ],
				 'filter': [ 
				 	{ 'range': { '@timestamp': { 'gte': 'now-7d/d', 'lte': 'now/d' }}}
				 ]
			}
		}
    }

    data = es.search_documents(indices, query)
    #print(data)
    print(json.dumps(data, indent=1))
