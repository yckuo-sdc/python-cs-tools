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

    def get(self, request_ip, field_name=""):
        url = self.host + "/json"

        if isinstance(request_ip, list):
            payload = {'ip': ','.join(request_ip)}
        else:
            payload = {'ip': request_ip}

        headers = {
            "content-type": "application/x-www-form-urlencoded",
        }

        try:
            data = requests.post(url,
                                     data=payload,
                                     headers=headers,
                                     timeout=10).json()
        except Exception as e:
            print(e)
            return False

        if not isinstance(request_ip, list):
            data = next(iter(data), None)

        if field_name:
            return data.get(field_name, False)

        return data

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

    def is_gov(self, ip):
        if not ip:
            return False

        gov_data = self.get(ip)

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
    print(ip2gov.get(ip, 'ACC'))
    print(ip2gov.get(ip))
    ip_list = [
        '60.248.16.43', '1.34.129.67', '1.34.74.153', '62.122.184.157',
    ]
    print(ip2gov.get(ip_list))
