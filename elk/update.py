<<<<<<< HEAD
import json
from elasticsearch import Elasticsearch


def connect_elasticsearch():
    _es = None
    _es = Elasticsearch(
        [{'host': 'localhost', 'port': 9200}] 
=======
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
import json
import os

def connect_elasticsearch():
    load_dotenv()
    host = os.getenv("DOCKER_ES_HOST")
    port = os.getenv("DOCKER_ES_PORT")
    username = os.getenv("DOCKER_ES_USERNAME")
    password = os.getenv("DOCKER_ES_PASSWORD")

    _es = None
    _es = Elasticsearch(
        [{'host': host, 'port': port}],
        http_auth=('username', 'password')
>>>>>>> d685d30d0b8feceef2997fa8f89bdaa4bcc24c4c
        )
    if _es.ping():
        print('Yay Connected')
    else:
        print('Awww it could not connect!')
    return _es


def search_record(es_object, index, query):

    try:
        result= es_object.search(index=index, body=query)
    except Exception as ex:
        print('Error in indexing data')
        print(str(ex))
    finally:
        return result


if __name__ == '__main__':
    es = connect_elasticsearch()

    # define the update data
    update_data = {    
        'doc': {        
            'NAME': 'LeJames3',
            'DOJ': '2003-04-04'
        }
    }

    # update the document
    es.update(index='company', id=1, body=update_data) 
