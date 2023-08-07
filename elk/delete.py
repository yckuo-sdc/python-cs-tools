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

    # delete the document with ID 1 from the index 'my_index'
    es.delete(index='company', id=1)


    # delete all documents in the index 'my_index' that match the query
    #es.delete_by_query(index='company', body={'query': {'match_all': {}}})
