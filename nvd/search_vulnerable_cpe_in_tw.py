"""Module detect nvd events and send alert mail."""
#!/usr/bin/python3
import argparse
import os
import sys

import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

#pylint: disable=wrong-import-position
from mail.send_mail import SendMail
from package.ip2gov_adapter import Ip2govAdapter
from package.nvd_adapter import NVDAdapter
from package.shodan_adapter import ShodanAdapter

#pylint: enable=wrong-import-position

parser = argparse.ArgumentParser()
parser.add_argument('--cve-id', help='The CVE ID (e.g. CVE-2023-36845)')

args = parser.parse_args()

if args.cve_id is None:
    print('The CVE ID must be provided (e.g. --cve-id CVE-2023-36845)')
    sys.exit(0)

CVE_ID = args.cve_id

if __name__ == '__main__':
    mail = SendMail()
    mail.set_predefined_recipient("nvd_alert")
    ip2gov = Ip2govAdapter()
    nvd = NVDAdapter()
    sa = ShodanAdapter()

    params = {
        'cveId': CVE_ID,
    }

    print("Search cves...")
    cves = nvd.get_cves(params)
    parsed_cves = nvd.parse_cve_fields(cves)
    print("Search cpe match strings in cves...")
    cpes_in_cves = nvd.get_cpe_matches_in_cves(parsed_cves)

    frames = []
    for cve in parsed_cves:
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

    path_to_csv = os.path.join(os.path.dirname(__file__), "..", "data",
                               "search_vulnerable_cpe_in_tw.csv")
    df.to_csv(path_to_csv, index=False, encoding='utf-8-sig')
