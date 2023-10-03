"""Module detect webshell and send alert mail."""
#!/usr/bin/python3
import os

import pandas as pd
from elasticsearch_dsl import Q, Search

import helper.http_validator as http
from package.elasticsearch_dsl_adapter import ElasticsearchDslAdapter

es = ElasticsearchDslAdapter()

GTE = "now-1y/y"
LT = "now/y"
BUCKETS_SIZE = 1000

q = Q("match", evtSubCat="Trojan")

s = Search(using=es.get_es_node(), index='new_ddi_2023.*') \
    .sort({"@timestamp": {"order": "desc"}})
    #.query(q) \
#.filter("range", **{'@timestamp':{"gte": GTE,"lt": LT}}) \

s.aggs.bucket('useragents',
              'terms',
              field='requestClientApplication.keyword',
              size=BUCKETS_SIZE,
              )

s = s[0:0]
response = s.execute()

print(s.to_dict())
print(f"Total Hits: {response.hits.total}")

bot_useragents = []
for useragent in response.aggregations.useragents.buckets:
    print(useragent.key, useragent.doc_count)
    if http.is_bot_useragent(useragent.key):
        bot_useragents.append(useragent.key)

print(bot_useragents)

df = pd.DataFrame(bot_useragents)
path_to_csv = os.path.join(os.path.dirname(__file__), "data",
                           "bot_useragents.csv")
df.to_csv(path_to_csv, index=False, encoding='utf-8-sig')
