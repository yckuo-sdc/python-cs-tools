"""Module detect gsn events and send alert mail."""
#!/usr/bin/python3
import os
import sys

import dateparser
import pandas as pd
import yaml

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

#pylint: disable=wrong-import-position
from mail.send_mail import SendMail
from package.gsn_search_adapter import GsnSearchAdapter

#pylint: enable=wrong-import-position


def parse_rules(yaml_file_path):
    """Functions"""
    with open(yaml_file_path, 'r', encoding='utf-8') as yaml_file:
        rules = yaml.safe_load(yaml_file)

    return rules


def parse_query_indicator(data):
    """Functions"""
    indicators = []
    excluded_indicators = []
    for key, value in data.items():
        if key == 'excluded':
            excluded_indicators.extend(value)
            continue

        indicators.extend(value)

    unique_indicators = list(set(indicators) - set(excluded_indicators))

    return unique_indicators


if __name__ == "__main__":

    mail = SendMail()
    mail.set_predefined_recipient("gsn_alert")
    #mail.set_predefined_recipient("test")
    gs = GsnSearchAdapter()

    PATH_TO_YAML = os.path.join(os.path.dirname(__file__), "rule",
                                "gsn_alert.yml")
    gsn_alerts = parse_rules(PATH_TO_YAML)

    for gsn_alert in gsn_alerts:
        try:
            print(gsn_alert['title'])
            search = gsn_alert['search']
            api_type = search.get('api_type')
            start_date_string = search.get('start_date')
            end_date_string = search.get('end_date')
            query_indicator = search.get('query_indicator')

            start_date = dateparser.parse(start_date_string).strftime(
                "%Y-%m-%d")
            end_date = dateparser.parse(end_date_string).strftime("%Y-%m-%d")
            parsed_query_indicator = parse_query_indicator(query_indicator)

            records = gs.get(api_type, parsed_query_indicator, start_date, end_date)
            print(f"Records found: {len(records)}")

            df = pd.DataFrame(records)

            if df.empty:
                print('DataFrame is empty!')
                continue

            if 'query_DN' in df.columns:
                df['query_DN'] = df['query_DN'].str.replace('.', '[.]')

            DF_SORTED = df.sort_values(by='count', ascending=False)
            SUBJECT = f"GSN Alert: {gsn_alert['title']}"
            TABLE = DF_SORTED.to_html(justify='left',
                                      index=False,
                                      escape=False)

            replacement = {"table": TABLE}
            TEMPLATE_HTML = "rwd_ddi.html"

            mail.set_subject(SUBJECT)
            mail.set_template_body_parser(replacement, TEMPLATE_HTML)
            mail.send()
        except Exception as e:
            print(e)
