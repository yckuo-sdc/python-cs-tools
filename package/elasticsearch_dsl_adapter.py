import json
import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search


class ElasticsearchDslAdapter():   

    def __init__(self,  host="", port=""): 
        if host == "" or port == "":
            load_dotenv()
            self.host = os.getenv("DDI_ES_HOST")
            self.port = os.getenv("DDI_ES_PORT")
        else:
            self.host = host 
            self.port = port
            
        self.__es = None
        self.__es = Elasticsearch([{ 'host': self.host, 'port': self.port }])

        if self.__es.ping():
            print('Yay Connected')
        else:
            print('Awww it could not connect!')
            os._exit(0) 

    def get_es_node(self):
        return self.__es

    def search_sample(self):
        s = Search(using=self.__es, index='new_ddi*') \
            .query("match", ruleName="Response") \
            .sort({"@timestamp": {"order": "desc"}})    

        s.aggs.bucket('useragents', 'terms', field='requestClientApplication.keyword') \

        s = s[0:30]

        response = s.execute()

        print(s.to_dict())
        print(response["hits"]["total"])  

        for id_hit, hit in enumerate(response['hits']['hits']):
            print((id_hit+1), hit['_source']['ruleName'])
        
        for tag in response['aggregations']['useragents']['buckets']:
            print(tag['key'], tag['doc_count'])

    def search_documents(self, index, query):
        data = {}
        try:
            result= self.__es.search(index=index, body=query)
            #print(result)
        except Exception as e:
            print('Error in indexing data')
            print(str(e))
        finally:
            data['total'] = result['hits']['total'] 
            data['documents'] = result['hits']['hits']
            return data

    def aggregate_documents(self, index, query, tag_name):
        data = {}
        try:
            result= self.__es.search(index=index, body=query)
        except Exception as e:
            print('Error in indexing data')
            print(str(e))
        finally:
            print(result)
            buckets = result['aggregations'][tag_name]['buckets']
            data['total'] = len(buckets)
            data['buckets'] = buckets
            return data 

if __name__ == '__main__':
    es = ElasticsearchDslAdapter()

