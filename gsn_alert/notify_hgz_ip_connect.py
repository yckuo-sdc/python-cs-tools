"""Module detect ddi events and send alert mail."""
#!/usr/bin/python3
import os
import sys
from datetime import datetime, timedelta

import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

#pylint: disable=wrong-import-position
from mail.send_mail import SendMail
from package.gsn_search_adapter import GsnSearchAdapter

#pylint: enable=wrong-import-position

if __name__ == "__main__":

    mail = SendMail()
    mail.set_predefined_recipient("gsn_alert")
    gs = GsnSearchAdapter()

    query_data = [
        '106.55.151.203',
        '170.106.11.252',
        '124.156.201.241',
        '129.204.188.155',
        '58.87.106.10',
        '152.136.84.245',
        '43.138.87.107',
        '188.131.243.141',
        '152.136.134.211',
        '58.87.84.224',
        '49.234.108.57',
        '42.194.253.227',
        '42.194.252.245',
    ]


    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    API_TYPE = 'ip_connect_count'
    START_DATE = yesterday
    END_DATE = today

    records = gs.get(API_TYPE, query_data, START_DATE, END_DATE)
    print(f"Records found: {len(records)}")

    df = pd.DataFrame(records)
    DF_SORTED = df.sort_values(by='count', ascending=False)

    SUBJECT = "GSN Alert: Huigezi Ip Hit"
    TABLE = DF_SORTED.to_html(justify='left', index=False)

    mail.set_subject(SUBJECT)
    mail.set_template_body(mapping=TABLE)
    mail.send()
