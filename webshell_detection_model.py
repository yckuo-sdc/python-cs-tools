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
    ip2gov = Ip2govAdapter()
    bt = BoturlValidator()

    label_keys = ['is_gov', 'network_reachable', 'http_success', 'filehash_malicious', 'boturl_malicious'] 
    labels = []
    for doc in docs:
        default_value = False
        label = dict.fromkeys(label_keys, default_value)

        service = network.get_service_info(doc)

        if early_stopping:
            label['is_gov'] = ip2gov.is_gov(service['ip'])
            if label['is_gov']:
                label['network_reachable'] = network.is_opened(doc['dst'], int(doc['dpt']))
                label['http_success'] = http.is_successful(doc['request'])
                if label['http_success']:
                    label['filehash_malicious'] = vt.is_malicious_by_filehash(filehash)
                    label['boturl_malicious'] = bt.is_malicious_by_boturl(doc['request'], doc['cs8'])
        else: 
            label['is_gov'] = ip2gov.is_gov(service['ip'])
            label['network_reachable'] = network.is_opened(doc['dst'], int(doc['dpt']))
            label['http_success'] = http.is_successful(doc['request'])
            label['filehash_malicious'] = vt.is_malicious_by_filehash(doc['fileHash'])
            label['boturl_malicious'] = bt.is_malicious_by_boturl(doc['request'], doc['cs8'])

        labels.append(label)

    labels = func.arr_dict_to_flat_dict(labels)

    return labels
