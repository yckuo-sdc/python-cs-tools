import json
from elasticsearch import Elasticsearch


def connect_elasticsearch():
    _es = None
    _es = Elasticsearch(
        [{'host': 'localhost', 'port': 9200}] 
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
