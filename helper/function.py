"""Module"""
import json
import os
import sys
import urllib

import numpy as np
import pandas as pd


def filter_hits_by_keys(hits, selected_keys):
    """Functions"""
    filtered_source_data = []
    for hit in hits:
        source_data = hit._source
        doc = {}
        for key in selected_keys:
            if key in source_data:
                doc[key] = source_data[key]
            else:
                doc[key] = None
        filtered_source_data.append(doc)

    return filtered_source_data


def arr_dict_to_flat_dict(arr_dict):
    """Functions"""
    flat_dict = {}
    for my_dict in arr_dict:
        for key in my_dict:
            try:
                flat_dict[key] = np.append(flat_dict[key], my_dict[key])
            except KeyError:
                flat_dict[key] = np.array([my_dict[key]])

    return flat_dict


def extract_ip(ip_st):
    """Functions"""
    ip_list = ip_st.split()

    return ip_list[0]


def convert_to_date(datetime_str):
    """Functions"""
    datetime_obj = pd.to_datetime(datetime_str)

    # Extract the date part using the .dt.date attribute
    date_only = datetime_obj.date()

    # Convert the date object back to a string if needed
    date_str = date_only.strftime('%Y-%m-%d')
    return date_str

def get_direction_by_rulename(rulename):
    """Functions"""
    if "response" in rulename.lower():
        return "response"

    if "request" in rulename.lower():
        return "request"

    return "both"


def get_download_http_record_url(ddi_df):
    """Functions"""
    host = os.getenv("FLASK_HOST")
    url = None

    new_df = pd.DataFrame()
    new_df['date'] = ddi_df['rt'].apply(convert_to_date)
    new_df['src'] = ddi_df['src'].apply(extract_ip)
    new_df['dst'] = ddi_df['dst'].apply(extract_ip)
    new_df['direction'] = ddi_df['ruleName'].apply(get_direction_by_rulename)

    unique_df = new_df.drop_duplicates(subset=['date', 'src', 'dst', 'direction'])

    query_data = unique_df.to_dict(orient='records')
    query_data_json = json.dumps(query_data)

    params = {'query_data': query_data_json}
    encoded_params = urllib.parse.urlencode(params)
    url = f"{host}/api/download?{encoded_params}"

    return url
