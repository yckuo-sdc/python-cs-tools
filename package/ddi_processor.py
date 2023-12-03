"""Module"""
import os
import sys
from datetime import datetime

import pandas as pd
import pytz

sys.path.append(os.path.dirname(__file__))

#pylint: disable=wrong-import-position
from ip2gov_adapter import Ip2govAdapter

#pylint: enable=wrong-import-position


class DDIProcessor:

    def __init__(self):
        self.date_fields = ['rt', '@timestamp']
        self.selected_fields = [
            'rt', 'ruleName', 'reason', 'evtSubCat', 'Serverity', 'request',
            'cs8', 'fname', 'fileHash', 'requestClientApplication', 'src',
            'dst', 'spt', 'dpt'
        ]
        self.ip2gov = Ip2govAdapter()

    def set_selected_fields(self, selected_fields):
        self.selected_fields = selected_fields

    def get_selected_fields(self):
        return self.selected_fields

    def filter_all_hits_by_selected_fields(self, hits):
        filtered_hits = []
        for hit in hits:
            doc = {}
            for field in self.selected_fields:
                if field in hit:
                    doc[field] = hit[field]
                else:
                    doc[field] = None
            filtered_hits.append(doc)

        filtered_hits.sort(key=lambda x: x['rt'], reverse=True)

        return filtered_hits

    def enrich_dataframe(self, dataframe):
        # Enrich ip with organization name
        dataframe['src'] = dataframe['src'].apply(
            lambda x: f"{x} {self.ip2gov.get(x, 'ACC')}")
        dataframe['dst'] = dataframe['dst'].apply(
            lambda x: f"{x} {self.ip2gov.get(x, 'ACC')}")

        for field in self.date_fields:
            if field in dataframe.columns:
                # Sort by date field
                dataframe = dataframe.sort_values(by=field, ascending=False)

                # Convert a UTC timestamp string to local time
                local_timezone = 'Asia/Taipei'
                dataframe[field] = pd.to_datetime(dataframe[field], utc=True)
                dataframe[field] = dataframe[field].dt.tz_convert(
                    local_timezone)
                dataframe[field] = dataframe[field].dt.strftime("%Y-%m-%d %H:%M:%S")

                break

        return dataframe


if __name__ == '__main__':
    dp = DDIProcessor()
    print(dp.get_selected_fields())
