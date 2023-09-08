import json

from package.elasticsearch_adapter import ElasticsearchAdapter

es = ElasticsearchAdapter()

indices = 'new_ddi_2023.*'

# define the search query
query = {    
    'from': 0,
    'size': 10,
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
    }
}

data = es.search_documents(indices, query)
print(json.dumps(data, indent=1))

