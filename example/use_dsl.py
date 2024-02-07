"""Module"""
from datetime import datetime
from elasticsearch import Elasticsearch
from elasticsearch_dsl import UpdateByQuery, Q

# Connect to Elasticsearch
client = Elasticsearch(['10.3.40.16'])

# Get current date and time in ISO format
current_date = datetime.now().isoformat()

q = Q('bool',
    must_not=[Q("exists", field="pushed_at")]
)

# Update documents matching the query
ubq = UpdateByQuery(using=client, index='hacker_news_analyze_by_gemini') \
      .query(q) \
      .script(
            source="ctx._source.pushed_at = params.new_date",
            params={
                'refresh': 'true',
                'new_date': current_date,
            }
        )

response = ubq.execute()
print(ubq.to_dict())
