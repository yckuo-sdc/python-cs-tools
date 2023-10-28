"""Module Proof of Concept for CVE-2018-17020."""
import os
import socket

import pandas as pd
import requests

import helper.function as func
import helper.http_validator as http
from package.ip2gov_adapter import Ip2govAdapter
from package.shodan_adapter import ShodanAdapter

if __name__ == '__main__':

    ip2gov = Ip2govAdapter()
    sa = ShodanAdapter()


    path_to_csv = os.path.join(os.path.dirname(__file__), "data",
                               "ip_list.csv")

    data = pd.read_csv(path_to_csv)

    specific_column = data['ip']
    ip_list = specific_column.tolist()

    segment_size = 10
    segmented_lists = [ip_list[i:i+segment_size] for i in range(0, len(ip_list), segment_size)]

    results = []
    for segmented_list in segmented_lists:
        gov_data = ip2gov.get(segmented_list)
        print(gov_data)
        if gov_data:
            results.extend(gov_data)

    df = pd.DataFrame(results)
    path_to_csv = os.path.join(os.path.dirname(__file__), "data",
                               "use_ssh_ip.csv")
    df.to_csv(path_to_csv, index=False, encoding='utf-8-sig')
