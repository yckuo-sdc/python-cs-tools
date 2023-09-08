import json

from elasticsearch import Elasticsearch


def connect_elasticsearch():
    _es = None
    _es = Elasticsearch(
        [{'host': '10.3.40.21', 'port': 9200}], 
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

    # define the search query
    query = {    
        'size': 1000,
		'query': {
			'bool': { 
		    	'must': [ 
					{
                        'match': {            
						    'Serverity': '4'        
					    }
                    }
				 ],
				 'filter': [ 
				 	{ 
						'range': { 
							'@timestamp': 
								{ 'gte': 'now-90d/d', 'lte': 'now/d'}
						}
					}
				  ]
			}
		}
    }

    # match query
    #query = {    
    #    'size': 1000,
	#	'query': {
    #        'match': {            
    #            'Serverity': '4'
    #         }
    #    }
    #}

    # range query
    #query = {    
    #    'size': 1000,
	#	'query': {
    #        'range': {            
	#		    '@timestamp': 
	#			    { 'gte': 'now-90d/d', 'lte': 'now/d'}
    #         }
    #    }
    #}

    result = search_record(es, 'new_ddi*', query)
    print(json.dumps(result, indent=1))
