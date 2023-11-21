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
mail.set_nvd_alert_recipients()
ip2gov = Ip2govAdapter()
nvd = NVDAdapter()
sa = ShodanAdapter()

params = {
    'cveId': 'CVE-2023-20198',
}

print("Search cves...")
cves = nvd.get_cves(params)
parsed_cves = nvd.parse_cve_fields(cves)
print("Search match strings in cves...")
cpes_in_cves = nvd.get_cpe_matches_in_cves(parsed_cves)

cpe_list = list(cpes_in_cves.values())
match_string_num = sum(len(c) for c in cpe_list)
print(f"Match strings found: {match_string_num}")

frames = []
for cve in parsed_cves:
    cpe_matches = cpes_in_cves[cve['cve_id']]
    unique_cpe_matches = list(set(cpe_matches))

    results = []
    for cpe_match in unique_cpe_matches:
        search_filter = {'cpe': cpe_match, 'country': 'tw'}
        hit_number = sa.get_hit_number(search_filter)
        if not hit_number:
            continue

        results.append({
            'tw_hits': hit_number,
            'vulnerable_cpe': cpe_match
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

#SUBJECT = "NVD Alert: Vulnerable CPE in TW"
#TABLE = total_df.to_html(justify='left', index=False)
#
#mail.set_subject(SUBJECT)
#mail.set_template_body(mapping=TABLE)
#mail.send()
