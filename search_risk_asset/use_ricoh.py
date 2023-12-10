"""Module Proof of Concept Ricoh Service."""
import datetime
import os
import sys

import pandas as pd
import requests

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

#pylint: disable=wrong-import-position
import helper.network_validator as network

#pylint: enable=wrong-import-position

if __name__ == '__main__':

    path_to_csv = os.path.join(os.path.dirname(__file__), "..", "data",
                               "use_shodan_and_ipdn.csv")

    fields = pd.read_csv(path_to_csv).to_dict(orient='records')
    print(f"Records found: {len(fields)}")

    label_keys = ['is_opened', 'timestamp']
    output = []
    for field in fields:
        DEFAULT_VALUE = None
        label = dict.fromkeys(label_keys, DEFAULT_VALUE)

        label['is_opened'] = network.is_opened(field['ip'], field['port'])
        now = datetime.datetime.now()
        label['timestamp'] = now.strftime("%Y-%m-%d %H:%M:%S")
        output.append(field | label)

    df = pd.DataFrame(output)
    path_to_csv = os.path.join(os.path.dirname(__file__), "..", "data",
                               "use_ricoh.csv")
    df.to_csv(path_to_csv, index=False, encoding='utf-8-sig')
