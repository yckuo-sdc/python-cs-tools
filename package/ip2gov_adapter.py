from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import json
import os

class Ip2govAdapter:   

    def __init__(self,  host=""): 
        if host == "":
            load_dotenv()
            self.host = os.getenv("IP2GOV_HOST")
        else:
            self.host = host 
            
    def get_gov_data_by_ip(self, ip):
      url = self.host + "/json"

      try:
          payload = {'ip': ip}
          headers = {
              "content-type": "application/x-www-form-urlencoded",
          }
          response = requests.post(url, data=payload, headers=headers, timeout=10).json()
      except Exception as e:
        print(e)
        return False

      gov_data = next(iter(response), None)

      return gov_data

    def get_gov_data_by_ip_list(self, ip_list):
      url = self.host + "/json"

      try:
          payload = {'ip': ','.join(ip_list)}
          headers = {
              "content-type": "application/x-www-form-urlencoded",
          }
          response = requests.post(url, data=payload, headers=headers, timeout=10).json()
      except Exception as e:
        print(e)
        return False

      gov_data = response

      return gov_data

    def is_gov(self, ip):
      if not ip:
        return False

      gov_data = self.get_gov_data_by_ip(ip)
      print(gov_data)

      if not gov_data:
        return False

      if gov_data['CC'] != 'TW':
        return False

      if gov_data['ASN'] != '4782':
        return False
        
      return True

if __name__ == '__main__':
    ip2gov = Ip2govAdapter()

    ip = '61.57.37.60'
    print(ip2gov.is_gov(ip))
    print(ip2gov.get_gov_data_by_ip_list(['8.8.8.8', '210.69.40.156']))
