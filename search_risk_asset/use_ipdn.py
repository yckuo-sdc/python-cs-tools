"""Module Proof of Concept for CVE-2023-20198."""
import os
import sys

import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

#pylint: disable=wrong-import-position
from package.ip2gov_adapter import Ip2govAdapter
from package.shodan_adapter import ShodanAdapter

#pylint: enable=wrong-import-position

if __name__ == '__main__':

    ip2gov = Ip2govAdapter()
    path_to_csv = os.path.join(os.path.dirname(__file__), "..", "data",
                               "ip4net.csv")
    fields = pd.read_csv(path_to_csv).to_dict(orient='records')
    print(f"Records found: {len(fields)}")

    output = []
    for field in fields:
        label = ip2gov.get(field['ip'])
        output.append(field | label)

    df = pd.DataFrame(output)

    path_to_csv = os.path.join(os.path.dirname(__file__), "..", "data",
                               "use_ip4net.csv")
    df.to_csv(path_to_csv, index=False, encoding='utf-8-sig')
