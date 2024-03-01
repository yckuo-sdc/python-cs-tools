"""Module detect nvd events and send alert mail."""
#!/usr/bin/python3
import os
import sys
from datetime import datetime, timedelta

import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

#pylint: disable=wrong-import-position
from mail.send_mail import SendMail
from package.ip2gov_adapter import Ip2govAdapter
from package.nvd_adapter import NVDAdapter
from package.shodan_adapter import ShodanAdapter

#pylint: enable=wrong-import-position

mail = SendMail()
mail.set_predefined_recipient("nvd_alert")
ip2gov = Ip2govAdapter()
nvd = NVDAdapter()
sa = ShodanAdapter()

pub_end_date = datetime.now()
pub_start_date = pub_end_date - timedelta(days=7)
selected_severities = ['CRITICAL', 'HIGH']

cves = nvd.get_cves_with_cpes(pub_start_date, pub_end_date,
                              selected_severities)

df = pd.DataFrame(cves)
print(df)

if df.empty:
    print('DataFrame is empty!')
    sys.exit(0)

SUBJECT = "NVD Alert: New CVE with Affected CPE"
TABLE = df.to_html(justify='left', index=False)

replacement = {"table": TABLE}
TEMPLATE_HTML = "rwd_ddi.html"

mail.set_subject(SUBJECT)
mail.set_template_body_parser(replacement, TEMPLATE_HTML)
mail.send()
