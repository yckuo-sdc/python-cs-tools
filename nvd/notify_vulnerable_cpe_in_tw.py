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
selected_severities = [
    'CRITICAL', 
    'HIGH',
]

print("Search cves with vulnerable cpe...")
cves = nvd.get_cves_with_cpes(pub_start_date, pub_end_date,
                              selected_severities)
print("Search cpe match strings in cves...")
cpes_in_cves = nvd.get_cpe_matches_in_cves(cves)

frames = []
for cve in cves:
    cpe_matches = cpes_in_cves[cve['cve_id']]

    results = []
    for cpe_match in cpe_matches:
        search_filter = {'cpe': cpe_match['criteria'], 'country': 'tw'}
        hit_number = sa.get_hit_number(search_filter)

        if not hit_number:
            continue

        results.append({
            'tw_hits': hit_number,
            'vulnerable_cpe': cpe_match['criteria']
        } | cve)

        if not cpe_match['match_strings']:
            continue

        for match_string in cpe_match['match_strings']:
            search_filter = {'cpe': match_string, 'country': 'tw'}
            hit_number = sa.get_hit_number(search_filter)

            if not hit_number:
                continue

            results.append({
                'tw_hits': hit_number,
                'vulnerable_cpe': match_string
            } | cve)


    df = pd.DataFrame(results)
    frames.append(df)

total_df = pd.DataFrame()
try:
    total_df = pd.concat(frames, ignore_index=True)
    print(total_df)
except pd.errors.MergeError as e:
    print(e)

if total_df.empty:
    sys.exit('DataFrame is empty!')

SUBJECT = "NVD Alert: Vulnerable CPE in TW"
TABLE = total_df.to_html(justify='left', index=False)

replacement = {"table": TABLE}
TEMPLATE_HTML = "rwd_ddi.html"

mail.set_subject(SUBJECT)
mail.set_template_body_parser(replacement, TEMPLATE_HTML)
mail.send()
