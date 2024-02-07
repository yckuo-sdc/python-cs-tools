"""Module detect ddi events and send alert mail."""
#!/usr/bin/python3
import os
import sys
from io import BytesIO

import pandas as pd
import yaml
from elasticsearch_dsl import ElasticsearchDslException, Search

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

#pylint: disable=wrong-import-position
from mail.send_mail import SendMail
from package.elasticsearch_dsl_adapter import ElasticsearchDslAdapter
from package.gsn_search_adapter import GsnSearchAdapter
from package.ip2gov_adapter import Ip2govAdapter
from package.new_ddi_processor import DDIProcessor

#pylint: enable=wrong-import-position


def parse_rules(yaml_file_path):
    """Functions"""
    with open(yaml_file_path, 'r', encoding='utf-8') as yaml_file:
        rules = yaml.safe_load(yaml_file)

    return rules


def extract_ip(ip_st):
    """Functions"""
    ip_list = ip_st.split()

    return ip_list[0]


def convert_to_date(datetime_str):
    """Functions"""
    datetime_obj = pd.to_datetime(datetime_str)

    # Extract the date part using the .dt.date attribute
    date_only = datetime_obj.date()

    # Convert the date object back to a string if needed
    date_str = date_only.strftime('%Y-%m-%d')
    return date_str


def get_gsn_http_record_df(ddi_df):
    """Functions"""
    df = pd.DataFrame()
    df['date'] = ddi_df['rt'].apply(convert_to_date)
    df['src'] = ddi_df['src'].apply(extract_ip)
    df['dst'] = ddi_df['dst'].apply(extract_ip)

    unique_df = df.drop_duplicates(subset=['date', 'src', 'dst'])
    gsn_searchs = unique_df.to_dict(orient='records')

    api_type = 'ip_pair_http_record'
    frames = []
    for gsn_search in gsn_searchs:
        ip_pair = [gsn_search['src'], gsn_search['dst']]
        records = gs.get(api_type, ip_pair, gsn_search['date'],
                         gsn_search['date'])
        print(f"Records found: {len(records)}")
        frames.append(pd.DataFrame(records))

    merged_df = pd.DataFrame()
    try:
        merged_df = pd.concat(frames, ignore_index=True)
    except pd.errors.MergeError as err:
        print(err)

    return merged_df


if __name__ == "__main__":

    mail = SendMail()
    mail.set_predefined_recipient("test")
    es = ElasticsearchDslAdapter()
    ip2gov = Ip2govAdapter()
    dp = DDIProcessor()
    gs = GsnSearchAdapter()

    PATH_TO_YAML = os.path.join(os.path.dirname(__file__), "rule",
                                "test_alert.yml")
    ddi_alerts = parse_rules(PATH_TO_YAML)

    for ddi_alert in ddi_alerts:
        try:
            title = ddi_alert.get('title')
            print(title)

            search = ddi_alert.get('search')
            GTE = search.get('gte')
            LTE = search.get('lte')
            query = search.get('query')
            add_selected_fields = search.get('add_selected_fields')
            remove_selected_fields = search.get('remove_selected_fields')
            post_process_method = search.get('post_process_method')

            q = dp.combine_boolean_query(query)
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

            enriched_df = dp.enrich_dataframe(df)
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)

            if enriched_df.empty:
                print('DataFrame is empty!')
                continue

            print(enriched_df)

            csv_df = get_gsn_http_record_df(enriched_df)

            if not csv_df.empty:
                buffer = BytesIO()
                csv_df.to_csv(buffer, index=False, encoding='utf-8')
                buffer.seek(0)

                attachments = [{
                    'type': 'buffer',
                    'value': buffer,
                    'name': 'gsn_http_record.csv'
                }]
                mail.add_attachment(attachments)

            SUBJECT = f"New DDI Alert: {title}"
            TABLE = enriched_df.to_html(justify='left',
                                        index=False,
                                        escape=False)
            mail.set_subject(SUBJECT)
            mail.set_template_body(mapping=TABLE)
            mail.send()
        except ElasticsearchDslException as e:
            print(e)
