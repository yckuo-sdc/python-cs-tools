import json
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

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
    actions = []

    update_action = {
    	'_op_type': 'update',
    	'_index': 'company',
    	'_id': 1, 
    	'doc': {
            'NAME': 'LeJames1',
            'DOJ': '2020-04-03'
		}
    }

    # index_action = {
    #     '_op_type': 'index'         
    #     '_index': 'company', 
    #     '_id': 1,                  
    #     'doc': {                
    #         'NAME': 'Wade',
    #         'DOJ': '1999-04-03'
    #     }
    #     
    # }

	# delete_action = {
    #     '_op_type': 'delete', 
    #     '_index': 'company',
    #     '_id': 'qsYuynQBjyvRpz1FfbP9' 
    # }


    actions.append(update_action) 

    if actions:
        bulk(es, actions)
