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
                           "query_ip_pairs.csv")

df = pd.read_csv(path_to_csv)
srcs = df['src'].tolist()
dsts = df['dst'].tolist()

print(df)

API_TYPE = 'ip_pair_http_record'
START_DATE = '2023-11-26'
END_DATE = '2023-11-26'

frames = []
for src, dst in zip(srcs, dsts):
    records = gs.get(API_TYPE, [src, dst], START_DATE, END_DATE)
    print(f"Records found: {len(records)}")
    df = pd.DataFrame(records)
    frames.append(df)

total_df = pd.DataFrame()
try:
    total_df = pd.concat(frames, ignore_index=True)
except pd.errors.MergeError as e:
    print(e)

path_to_csv = os.path.join(os.path.dirname(__file__), "..", "data",
                           "do_query_ip_pairs.csv")
total_df.to_csv(path_to_csv, index=False, encoding='utf-8-sig')
