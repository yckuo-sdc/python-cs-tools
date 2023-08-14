#!/usr/bin/python3 
from package.ip2gov_adapter import Ip2govAdapter 
from package.virustotal import VirusTotal
from package.network_utility import NetworkUtility
import helper.http_validator as http
import helper.network_validator as network
import helper.function as func
import numpy as np

def get_webshell_labels(docs, flag=1):
    vt = VirusTotal()
    ip2gov = Ip2govAdapter()

    label_keys = ['is_gov', 'reachable', 'success', 'manipulated', 'malicious'] 
    labels = []
    for doc in docs:
        default_value = False
        label = dict.fromkeys(label_keys, default_value)

        if flag == 1:    
            net_utl = NetworkUtility(doc['request'])
            service = net_utl.get_service_info(doc)
            label['is_gov'] = ip2gov.is_gov(service['ip'])
            if label['is_gov']:
                label['reachable'] = net_utl.is_reachable()
                if label['reachable']:
                    label['success'] = http.is_successful(doc['request'])
                    if label['success']:
                        label['manipulated'] = http.is_manipulated(doc['requestClientApplication'])
                        label['malicious'] = False 
        elif flag == 2:
            service = network.get_service_info(doc)
            label['is_gov'] = ip2gov.is_gov(service['ip'])
            label['reachable'] = True
            if label['is_gov']:
                label['success'] = http.is_successful(doc['request'])
                if label['success']:
                    label['manipulated'] = http.is_manipulated(doc['requestClientApplication'])
                    label['malicious'] = False 

        labels.append(label)

    labels = func.arr_dict_to_flat_dict(labels)

    return labels

