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
        'ceshi.hgzvip.net',
        'custom.hgzvip.net',
        'dota.hgzvip.net',
        'down.hgzvip.net',
        'jiqunxx.hgzvip.net',
        'microsoft02.hgzvip.net',
        'microsoft03.hgzvip.net',
        'microsoft04.hgzvip.net',
        'omcs.hgzvip.net',
        'omcs02.hgzvip.net',
        'p2p01.hgzvip.net',
        'renzheng.hgzvip.net',
        'saas.hgzvip.net',
        'safe.hgzvip.net',
        'shengcheng.hgzvip.net',
        'spare.hgzvip.net',
        'unins.hgzvip.net',
        'update.hgzvip.net',
        'esdaili01.huigezi.org',
        'esdaili02.huigezi.org',
        'esdaili03.huigezi.org',
        'freees.huigezi.org',
        'freeupdate.huigezi.org',
        'shengcheng.huigezi.org',
        'shoujiapi.huigezi.org',
        'sjyzm.huigezi.org',
        'xiezhuupdate01.huigezi.org',
    ]

    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    API_TYPE = 'dns_client'
    START_DATE = yesterday
    END_DATE = today

    records = gs.get(API_TYPE, query_data, START_DATE, END_DATE)
    print(f"Records found: {len(records)}")

    df = pd.DataFrame(records)
    df['query_DN'] = df['query_DN'].str.replace('.', '[.]')
    DF_SORTED = df.sort_values(by='count', ascending=False)

    SUBJECT = "GSN Alert: Huigezi Dn Query"
    TABLE = DF_SORTED.to_html(justify='left', index=False)

    mail.set_subject(SUBJECT)
    mail.set_template_body(mapping=TABLE)
    mail.send()
