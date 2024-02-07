"""Module detect ddi events and send alert mail."""
#!/usr/bin/python3
import os
import sys
from datetime import datetime
from operator import attrgetter

from elasticsearch_dsl import (ElasticsearchDslException, Q, Search,
                               UpdateByQuery)

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

#pylint: disable=wrong-import-position
from mail.send_mail import SendMail
from package.elasticsearch_dsl_adapter import ElasticsearchDslAdapter

#pylint: enable=wrong-import-position

if __name__ == "__main__":

    mail = SendMail()
    mail.set_predefined_recipient("test")
    es = ElasticsearchDslAdapter(host="10.3.40.16", port="9200")

    selected_fields = [
        'News Title',
        'Published Date',
        'link',
        'Attack Target',
        'Malicious Campaign',
        'Malware',
        'Summary',
    ]

    GTE = "now-3d"
    LTE = "now"

    q = Q('bool',
        #must_not=[Q("exists", field="pushed_at")],
        must=[Q("exists", field="pushed_at")],
    )

    try:
        s = Search(using=es.get_es_node(), index='hacker_news_analyze_by_gemini') \
            .query(q) \
            .filter("range", **{'Published Date':{"gte": GTE,"lte": LTE}}) \
            .sort({"Published Date": {"order": "desc"}})

        response = s.execute()

        print(s.to_dict())
        print(f"Total Hits: {response.hits.total}")

        hits = s.scan()

        filtered_hits = []
        for hit in hits:
            doc = {}
            for field in selected_fields:
                try:
                    doc[field] = attrgetter(field)(hit)
                except AttributeError:
                    doc[field] = None
            filtered_hits.append(doc)

        filtered_hits.sort(key=lambda x: x['Published Date'])

        selected_fields.remove('News Title')
        # notify news with email
        for hit in filtered_hits:
            subject = f"RSS News with OpenAI: {hit['News Title']}"
            BODY = "<table style='border:none;text-align:left;'>"
            for field in selected_fields:
                BODY += "<tr style='vertical-align:top;'>"
                BODY += f"<th>{field}</th>"
                BODY += f"<td>{hit[field]}</td>"
                BODY += "</tr>"

            BODY += "</table>"

            mail.set_subject(subject)
            mail.set_body(BODY)
            mail.send()

        # Get current date and time in ISO format
        current_date = datetime.now().isoformat()

        # Update documents matching the query
        ubq = UpdateByQuery(using=es.get_es_node(), index='hacker_news_analyze_by_gemini') \
              .query(q) \
              .filter("range", **{'Published Date':{"gte": GTE,"lte": LTE}}) \
              .script(
                    source="ctx._source.pushed_at = params.new_date",
                    params={
                        'refresh': 'true',
                        'new_date': current_date,
                    }
                )

        response = ubq.execute()
        print(ubq.to_dict())

    except ElasticsearchDslException as e:
        print(e)
