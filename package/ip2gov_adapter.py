import json
import os

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv


class Ip2govAdapter:

    def __init__(self, host="", apikey=""):
        if host == "":
            load_dotenv()
            self.host = os.getenv("IP2GOV_HOST")
            self.apikey = os.getenv("IP2GOV_APIKEY")
        else:
            self.host = host
            self.apikey = apikey

    def get_gov_data_by_ip(self, ip, field_name=""):
        url = self.host + "/json"

        try:
            payload = {'ip': ip}
            headers = {
                "content-type": "application/x-www-form-urlencoded",
            }
            response = requests.post(url,
                                     data=payload,
                                     headers=headers,
                                     timeout=10).json()
        except Exception as e:
            print(e)
            return False

        gov_data = next(iter(response), None)

        if field_name:
            return gov_data.get(field_name, False)

        return gov_data

    def get_gov_data_by_gas_ip_list(self, ip_list):
        url = self.host

        try:
            payload = {
                'ip': ','.join(ip_list),
                'token': self.apikey,
            }

            headers = {
                'content-type': 'application/x-www-form-urlencoded',
            }
            response = requests.post(url,
                                     data=payload,
                                     headers=headers,
                                     timeout=30).json()
        except Exception as e:
            print(e)
            return False

        gov_data = response

        return gov_data

    def get_gov_data_by_ip_list(self, ip_list):
        url = self.host + "/json"

        try:
            payload = {'ip': ','.join(ip_list)}
            headers = {
                "content-type": "application/x-www-form-urlencoded",
            }
            response = requests.post(url,
                                     data=payload,
                                     headers=headers,
                                     timeout=10).json()
        except Exception as e:
            print(e)
            return False

        gov_data = response

        return gov_data

    def is_gov(self, ip):
        if not ip:
            return False

        gov_data = self.get_gov_data_by_ip(ip)

        if not gov_data:
            return False

        if gov_data['CC'] != 'TW':
            return False

        if gov_data['ASN'] != '4782':
            return False

        return True


if __name__ == '__main__':
    ip2gov = Ip2govAdapter()

    ip = '117.56.232.9'
    print(ip2gov.get_gov_data_by_ip(ip, 'ACC'))
    #ip_list = [
    #    '60.248.16.43', '1.34.129.67', '1.34.74.153', '62.122.184.157',
    #    '185.161.248.141', '62.122.184.156', '62.122.184.155',
    #    '62.122.184.154', '62.122.184.151', '62.122.184.153', '185.81.68.68',
    #    '185.81.68.67', '62.122.184.140', '62.122.184.159', '152.89.198.173',
    #    '185.234.216.154', '185.234.216.153', '185.234.216.155',
    #    '185.234.216.152', '185.234.216.150', '185.234.216.158',
    #    '185.234.216.156', '185.234.216.157', '185.234.216.159',
    #    '185.234.216.165', '185.234.216.160', '185.234.216.161',
    #    '185.234.216.178', '185.234.216.174', '185.234.216.175',
    #    '185.234.216.179', '185.234.216.163', '185.234.216.170',
    #    '185.234.216.162', '185.234.216.177', '185.234.216.187',
    #    '185.234.216.188', '185.234.216.171', '185.234.216.166',
    #    '185.234.216.168', '185.234.216.169', '185.234.216.173',
    #    '185.234.216.182', '185.234.216.180', '185.234.216.181',
    #    '62.122.184.158', '62.122.184.160', '62.122.184.161', '62.122.184.163',
    #    '62.122.184.162'
    #]
    #print(ip2gov.get_gov_data_by_ip_list(ip_list))

    #print(
    #    ip2gov.get_gov_data_by_gas_ip_list(
    #        ['117.56.232.9', '8.8.8.8', '210.69.40.156', '223.200.105.97']))
