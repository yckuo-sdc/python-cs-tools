"""Module"""
from datetime import datetime
from elasticsearch import Elasticsearch

# Connect to Elasticsearch
client = Elasticsearch(['10.3.40.16'])

# Get current date and time in ISO format
current_date = datetime.now().isoformat()

# Define your update query
q = {
     "script": {
        "inline": "ctx._source.pushed_at = params.new_date",
        "lang": "painless",
        "params": {
            "new_date": current_date,
            "refresh": "true",
        }
     },
     "query": {
        "bool": {
            "must_not": {
                "exists": {
                    "field":  "pushed_at"
                }
            }
        }
     }
}

client.update_by_query(body=q, doc_type='_doc', index='hacker_news_analyze_by_gemini')
