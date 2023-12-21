"""Module"""
import os
import sys

import pandas as pd
from elasticsearch_dsl import Q

sys.path.append(os.path.dirname(__file__))

#pylint: disable=wrong-import-position
from ip2gov_adapter import Ip2govAdapter
from shodan_adapter import ShodanAdapter
from virustotal import VirusTotal

#pylint: enable=wrong-import-position


class DDIProcessor:
    """This is a docstring that provides a brief description of MyClass."""

    def __init__(self):
        self.date_fields = ['rt', '@timestamp']
        self.selected_fields = [
            'rt',
            'ruleName',
            'reason',
            'evtSubCat',
            'Serverity',
            'app',
            'src',
            'dst',
            'spt',
            'dpt',
            'request',
            'fname',
            'fileHash',
            'requestClientApplication',
        ]
        self.exclude_acc_strings = ['蜜罐', 'Honeynet']

        self.ip2gov = Ip2govAdapter()
        self.vt = VirusTotal()
        self.sa = ShodanAdapter()

    def filter_hits_by_selected_fields(self, hits, selected_fields=None):
        """ This is a docstring that provides a brief description of my_function."""

        if selected_fields:
            fields = selected_fields.split(' ')
        else:
            fields = self.selected_fields

        filtered_hits = []
        for hit in hits:
            doc = {}
            for field in fields:
                if field in hit:
                    doc[field] = hit[field]
                else:
                    doc[field] = None
            filtered_hits.append(doc)

        filtered_hits.sort(key=lambda x: x['rt'], reverse=True)

        return filtered_hits

    def enrich_dataframe(self, dataframe):
        """ This is a docstring that provides a brief description of my_function."""

        # Enrich ip with organization name
        dataframe['src'] = dataframe['src'].apply(
            lambda x: f"{x} {self.ip2gov.get(x, 'ACC')}")
        dataframe['dst'] = dataframe['dst'].apply(
            lambda x: f"{x} {self.ip2gov.get(x, 'ACC')}")

        # Filter out exclude ACC strings
        dataframe = dataframe[
            ~dataframe['src'].str.contains('|'.join(self.exclude_acc_strings))
            &
            ~dataframe['dst'].str.contains('|'.join(self.exclude_acc_strings))]

        for field in self.date_fields:
            if field in dataframe.columns:
                # Sort by date field
                dataframe = dataframe.sort_values(by=field, ascending=False)

                # Convert a UTC timestamp string to local time
                local_timezone = 'Asia/Taipei'
                dataframe[field] = pd.to_datetime(dataframe[field], utc=True)
                dataframe[field] = dataframe[field].dt.tz_convert(
                    local_timezone)
                dataframe[field] = dataframe[field].dt.strftime(
                    "%Y-%m-%d %H:%M:%S")

                break

        return dataframe

    def combine_boolean_query(self, querys):
        """ This is a docstring that provides a brief description of my_function."""

        musts = []
        must_nots = []
        shoulds = []
        for query in querys:
            search_text_method = query.get('search_text_method')
            if search_text_method:
                query['search_text'] = self.solve_for(search_text_method)

            operator = query.get('operator')
            method = query.get('method')
            field_name = query.get('field_name')
            search_text = query.get('search_text')

            if operator == "must":
                musts.append(Q(method, **{field_name: search_text}))
            elif operator == "must_not":
                must_nots.append(Q(method, **{field_name: search_text}))
            elif operator == "should":
                shoulds.append(Q(method, **{field_name: search_text}))

        compound_query = Q('bool',
                           must=musts,
                           must_not=must_nots,
                           should=shoulds,
                           minimum_should_match=1)

        return compound_query

    def do_qnap_ips(self):
        """ This is a docstring that provides a brief description of my_function."""

        search_filter = {
            'product': 'qnap',
            'asn': 'AS4782',
        }

        match_field = [{'label': 'ip', 'field': 'ip_str'}]

        fields = self.sa.basic_query_cursor(search_filter, match_field)
        qnap_ip_list = [f['ip'] for f in fields]

        qnap_ips = ' '.join(qnap_ip_list)
        return qnap_ips

    def do_miner_request(self, **kwargs):
        """ This is a docstring that provides a brief description of my_function."""

        expected_keys = ['hits']

        unexpected_keys = set(kwargs.keys()) - set(expected_keys)
        if unexpected_keys:
            print(
                f"Unexpected keyword arguments: {', '.join(unexpected_keys)}")
            return None

        hits = kwargs['hits']
        selected_indices = [
            i for i, m in enumerate(hits) if self.ip2gov.is_gov(m['src'])
        ]
        selected_hits = [hits[i] for i in selected_indices]
        ips = [m['dst'] for m in selected_hits]
        labels = self.vt.get_malicious_number_by_ips(ips)

        filtered_fits = []
        for item1, item2 in zip(selected_hits, labels):
            if item2['vt_malicious_num']:
                filtered_fits.append(item1 | item2)

        return filtered_fits

    def solve_for(self, name: str, *args, **kwargs):
        """ This is a docstring that provides a brief description of my_function."""

        method_name = f"do_{name}"
        if hasattr(self, method_name) and callable(
                func := getattr(self, method_name)):
            response = func(*args, **kwargs)
            return response

        return None


if __name__ == '__main__':
    dp = DDIProcessor()
    print(dp.get_selected_fields())
    print(dp.solve_for('miner_request', hh=1))
    print(dp.solve_for('m_request', hits=[1, 2]))
