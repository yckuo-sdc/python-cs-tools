import json
from elasticsearch import Elasticsearch


def connect_elasticsearch():
    _es = None
    _es = Elasticsearch(
        [{'host': 'localhost', 'port': 9200}], 
        http_auth=('elastic', 'Kill0978021370!')
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
