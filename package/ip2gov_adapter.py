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

    def get_gov_data_by_ip(self, ip):
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

        return gov_data

    def get_gov_data_by_gas_ip_list(self, ip_list):
        url = self.host

        try:
            payload = {
                'ip': ','.join(ip_list),
                'token': self.apikey,
            }

            headers = {
                'content-type':
                'application/x-www-form-urlencoded',
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

    #ip = '61.57.37.60'
    #print(ip2gov.is_gov(ip))
    print(
        ip2gov.get_gov_data_by_gas_ip_list(
            ['117.56.232.9', '8.8.8.8', '210.69.40.156', '223.200.105.97']))
