#!/usr/bin/env python3
# coding: utf-8

import requests
import pandas as pd
import csv
import time

"""
print("=====================start=============================")
print(requests.get('http://10.3.41.130:5001/api_types').text)
print("=======================================================")
print(requests.get('http://10.3.41.130:5001/help').text)
print("=======================================================")
print(requests.get('http://10.3.41.130:5001/POST/task'))
print("=====================end===============================")
"""

def getlist_from_file(ioc_path):
    ioc_list = []
    with open(ioc_path, encoding='utf-8-sig') as f:
        csv_reader = csv.reader(f)
        for line in csv_reader:
            print(line)
            ioc_list.extend(line)
        return ioc_list

API_TYPE = 'ip_connect_count'
IOC_FILENAME = "/home/ubuntu/python/IP_LIST"
# QUERY_URL = ['http://117.56.7.248']
# QUERY_DN = getlist_from_file(IOC_FILENAME + ".csv")
# print("QUERY_DN Size: " + str(len(QUERY_DN)))
QUERY_IP = getlist_from_file(IOC_FILENAME + ".csv")
# print("QUERY_IP Size:" + str(QUERY_IP))

START_DATE = "2023-12-01"
END_DATE = "2023-12-08"
POST = {
            "API_type" : API_TYPE,
            # "URLs": QUERY_URL,
            # "DNs" : QUERY_DN,
            "IPs" : QUERY_IP,
            "start_date" : START_DATE,
            "end_date" : END_DATE,
        }

res = requests.post('http://10.3.41.130:5001/task', json = POST)
job_id = res.json()['data']['task_id']
print("job_id: " + str(job_id))

filename = str(START_DATE) + '_' + str(END_DATE) + '_' + str(API_TYPE) + str('.csv')

while(True):
    try:
        res = requests.get('http://10.3.41.130:5001/task/' + job_id)
        res_ = res.json()

        if res_['data']['task_status'] == 'finished':
            try:
                df = pd.DataFrame(res_['data']['task_result']['result'])
                df.to_csv(filename, encoding = 'utf-8-sig', index = False)
                print(filename + ' is done.')
                print(df.shape)
                break
            except Exception as e:
                print(e)
                df = pd.DataFrame.from_dict(res_['data']['task_result']['result'], orient='index')
                df.to_csv(filename, encoding = 'utf-8-sig', index = False)
        else:
            print("not finish:" + str(res_['data']))
            time.sleep(5)

    except:
        print("exception:" + str(res_))

# Cancel
# print(requests.get('http://10.3.41.130:5001/cancel_task/' + job_id).json())