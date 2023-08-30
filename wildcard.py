#!/usr/bin/python3 
from package.elasticsearch_dsl_adapter import ElasticsearchDslAdapter 
from elasticsearch_dsl import Search
from elasticsearch_dsl import Q

es = ElasticsearchDslAdapter()
wildcard = '*80'
q = ~Q('query_string', query='spt:'+wildcard, analyze_wildcard=True)
s = Search(using=es.get_es_node(), index='new_ddi_2023.*') \
    .query(q) \

#s = s[0:5]
#response = s.execute()

print(s.to_dict())


