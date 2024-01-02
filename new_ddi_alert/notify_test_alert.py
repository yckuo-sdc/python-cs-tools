"""Module detect ddi events and send alert mail."""
#!/usr/bin/python3
import os
import sys

import pandas as pd
import yaml
from elasticsearch_dsl import ElasticsearchDslException, Search

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

#pylint: disable=wrong-import-position
from mail.send_mail import SendMail
from package.elasticsearch_dsl_adapter import ElasticsearchDslAdapter
from package.ip2gov_adapter import Ip2govAdapter
from package.new_ddi_processor import DDIProcessor

#pylint: enable=wrong-import-position


def parse_rules(yaml_file_path):
    """Functions"""
    with open(yaml_file_path, 'r', encoding='utf-8') as yaml_file:
        rules = yaml.safe_load(yaml_file)

    return rules


if __name__ == "__main__":

    mail = SendMail()
    mail.set_predefined_recipient("test")
    es = ElasticsearchDslAdapter()
    ip2gov = Ip2govAdapter()
    dp = DDIProcessor()

    PATH_TO_YAML = os.path.join(os.path.dirname(__file__), "rule",
                                "test_alert.yml")
    ddi_alerts = parse_rules(PATH_TO_YAML)

    for ddi_alert in ddi_alerts:
        try:
            print(ddi_alert['title'])
            search = ddi_alert['search']
            GTE = search.get('gte')
            LTE = search.get('lte')
            add_selected_fields = search.get('add_selected_fields')
            remove_selected_fields = search.get('remove_selected_fields')
            post_process_method = search.get('post_process_method')

            q = dp.combine_boolean_query(search['query'])
            s = Search(using=es.get_es_node(), index='new_ddi*') \
                .query(q) \
                .filter("range", **{'@timestamp':{"gte": GTE,"lte": LTE}}) \
                .sort({"@timestamp": {"order": "desc"}})

            s = s[0:10]
            response = s.execute()

            print(s.to_dict())
            print(f"Total Hits: {response.hits.total}")

            hits = dp.filter_hits(s.scan(), add_selected_fields,
                                  remove_selected_fields)

            if post_process_method:
                hits = dp.solve_for(post_process_method, hits=hits)

            df = pd.DataFrame(hits)

            if df.empty:
                print('DataFrame is empty!')
                continue

            df = dp.enrich_dataframe(df)
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)

            print(df)

            SUBJECT = f"New DDI Alert: {ddi_alert['title']}"
            TABLE = df.to_html(justify='left', index=False, escape=False)

            mail.set_subject(SUBJECT)
            mail.set_template_body(mapping=TABLE)
            mail.send()
        except ElasticsearchDslException as e:
            print(e)
