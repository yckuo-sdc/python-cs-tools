"""Module update intelligence with virustotal."""
#!/usr/bin/python3
import os
import sys

import yaml

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

#pylint: disable=wrong-import-position
from package.virustotal import VirusTotal

#pylint: enable=wrong-import-position


def parse_rules(yaml_file_path):
    """Functions"""
    with open(yaml_file_path, 'r', encoding='utf-8') as yaml_file:
        rules = yaml.safe_load(yaml_file)

    return rules


def modify_rules(yaml_file_path, rules):
    """Functions"""
    with open(yaml_file_path, 'w', encoding='utf-8') as file:
        yaml.dump(rules,
                  file,
                  explicit_start=True,
                  default_flow_style=False,
                  sort_keys=False,
                  indent=None)


def parse_ioc(records):
    """Functions"""

    parsed_ioc = {'domain': [], 'ip': []}
    for record in records:
        parsed_ioc['domain'].append(record['domain'])
        parsed_ioc['ip'].extend(record['a_records'])

    parsed_ioc['domain'] = list(set(parsed_ioc['domain']))
    parsed_ioc['ip'] = list(set(parsed_ioc['ip']))

    return parsed_ioc


if __name__ == "__main__":

    vt = VirusTotal()

    hgzvip_net_records = vt.get_subdomain_and_a_records("hgzvip.net")
    huigezi_org_records = vt.get_subdomain_and_a_records("huigezi.org")

    # Merge the lists of dictionaries
    merged_records = hgzvip_net_records.copy()
    merged_records.extend(huigezi_org_records)

    ioc = parse_ioc(merged_records)

    PATH_TO_YAML = os.path.join(os.path.dirname(__file__), "rule",
                                "gsn_alert.yml")

    gsn_alerts = parse_rules(PATH_TO_YAML)

    hgz_titles =['Huigezi Ip Hit', 'Huigezi Dn Query']
    for gsn_alert in gsn_alerts:
        try:
            if gsn_alert['title'] in hgz_titles:
                print(gsn_alert['title'])
                ioc_type = gsn_alert['search']['ioc_type']
                print(f"ioc_type: {ioc_type}")
                gsn_alert['search']['query_indicator']['vt'] = ioc[ioc_type]

        except Exception as e:
            print(e)

    modify_rules(PATH_TO_YAML, gsn_alerts)
