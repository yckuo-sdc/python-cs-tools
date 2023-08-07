from elasticsearch import Elasticsearch

client = Elasticsearch("http://10.3.40.21:9200")
print(client.info())


res = client.search(index='new_ddi*', body={'query': {'match_all': {}}})

print(res)
