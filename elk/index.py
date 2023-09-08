import json
import os

from dotenv import load_dotenv
from elasticsearch import Elasticsearch


def connect_elasticsearch():
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


def store_record(es_object, index, data, id=0):
    is_stored = True

    try:
        if id: 
            outcome = es_object.index(index=index, body=json.dumps(data), id=id)
        else:
            outcome = es_object.index(index=index, body=json.dumps(data))
        print(outcome)
    except Exception as ex:
        print('Error in indexing data')
        print(str(ex))
        is_stored = False
    finally:
        return is_stored


if __name__ == '__main__':
    data = {
        'NAME': 'James2',
        'DOJ': '2003-04-02'
    }
    es = connect_elasticsearch()
    #result = store_record(es, 'company', data, 1)
    result = store_record(es, 'company', data)
    print(result)
