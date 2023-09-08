#!/usr/bin/python3 
import numpy as np


def filter_hits_by_keys(hits, selected_keys):
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
    flat_dict = {}
    for my_dict in arr_dict:
        for key in my_dict:
            try:
                flat_dict[key] = np.append(flat_dict[key], my_dict[key])
            except KeyError:
                flat_dict[key] = np.array([my_dict[key]])

    return flat_dict

