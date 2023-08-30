#!/usr/bin/python3 
from package.ip2gov_adapter import Ip2govAdapter 
from package.virustotal import VirusTotal
from package.boturl_validator import BoturlValidator
from package.network_utility import NetworkUtility
import helper.http_validator as http
import helper.network_validator as network
import helper.function as func
import numpy as np

def get_webshell_labels(docs, early_stopping=True):
    vt = VirusTotal()
    #ip2gov = Ip2govAdapter()
    bt = BoturlValidator()

    label_keys = ['http_success', 'filehash_malicious', 'boturl_malicious'] 
    labels = []
    for doc in docs:
        default_value = False
        label = dict.fromkeys(label_keys, default_value)
        service = network.get_service_info(doc)
        
        # Disable Early Stopping
        if not early_stopping:
            label['http_success'] = http.is_successful(doc['request'])
            label['filehash_malicious'] = vt.is_malicious_by_filehash(doc['fileHash'])
            label['boturl_malicious'] = bt.is_malicious_by_boturl(doc['request'], doc['cs8'])
            labels.append(label)
            continue


        # Enable Early Stopping
        if not http.is_successful(doc['request']):
            labels.append(label)
            continue

        label['http_success'] = True
        label['filehash_malicious'] = vt.is_malicious_by_filehash(filehash)
        label['boturl_malicious'] = bt.is_malicious_by_boturl(doc['request'], doc['cs8'])
        labels.append(label)

    labels = func.arr_dict_to_flat_dict(labels)

    return labels
