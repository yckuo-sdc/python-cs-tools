"""Module use gsn search."""
#!/usr/bin/python3
import os
import sys

import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

#pylint: disable=wrong-import-position
from package.gsn_search_adapter import GsnSearchAdapter

#pylint: enable=wrong-import-position

gs = GsnSearchAdapter()
path_to_csv = os.path.join(os.path.dirname(__file__), "..", "data",
                           "query_data.csv")

df = pd.read_csv(path_to_csv)
query_data = df['query_data'].tolist()

API_TYPE = 'ip_connect_count'
START_DATE = '2023-12-01'
END_DATE = '2023-12-07'

records = gs.get(API_TYPE, query_data, START_DATE, END_DATE)
print(f"Records found: {len(records)}")

df = pd.DataFrame(records)
path_to_csv = os.path.join(os.path.dirname(__file__), "..", "data",
                           "do_query_data.csv")
df.to_csv(path_to_csv, index=False, encoding='utf-8-sig')
