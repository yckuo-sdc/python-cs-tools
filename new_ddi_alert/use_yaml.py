"""Module detect ddi events and send alert mail."""
#!/usr/bin/python3
import os
import sys

import pandas as pd
from elasticsearch_dsl import Q, Search

import yaml

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

#pylint: disable=wrong-import-position
from mail.send_mail import SendMail
from package.ddi_processor import DDIProcessor
from package.elasticsearch_dsl_adapter import ElasticsearchDslAdapter
from package.ip2gov_adapter import Ip2govAdapter

#pylint: enable=wrong-import-position

def parse_rules(yaml_file_path):
    """Functions"""
    with open(yaml_file_path, 'r', encoding='utf-8') as yaml_file:
        rules = yaml.safe_load(yaml_file)

    return rules

if __name__ == "__main__":

    mail = SendMail()
    mail.set_ddi_alert_recipients()
    es = ElasticsearchDslAdapter()
    ip2gov = Ip2govAdapter()
    dp = DDIProcessor()

    PATH_TO_YAML = os.path.join(os.path.dirname(__file__), "yaml", "ddi_rule.yml")
    ddi_rules = parse_rules(PATH_TO_YAML)
    print(ddi_rules)

    GTE = "now-1h"
    LT = "now"

    for ddi_rule in ddi_rules:
        search = ddi_rule['search']
        GTE = search['gte']
        LTE = search['lte']

        query1 = next(iter(search['query']), None)
        q = Q(query1['method'], **{query1['field']: query1['keyword']})
        for query in search['query']:
            if query['operator'] == '&':
                q = q & Q(query['method'], **{query['field']: query['keyword']})
            elif query['operator'] == '|':
                q = q | Q(query['method'], **{query['field']: query['keyword']})

        s = Search(using=es.get_es_node(), index='new_ddi*') \
            .query(q) \
            .filter("range", **{'@timestamp':{"gte": GTE,"lt": LT}}) \
            .sort({"@timestamp": {"order": "desc"}})

        s = s[0:10]
        response = s.execute()

        print(s.to_dict())
        print(f"Total Hits: {response.hits.total}")
