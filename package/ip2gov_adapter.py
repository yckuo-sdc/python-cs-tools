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
            
    def get_gov_data(self, host):
      url = self.host + "/json"

      try:
          payload = {"ip": host}
          headers = {
              "content-type": "application/x-www-form-urlencoded",
          }
          response = requests.post(url, data=payload, headers=headers, timeout=10).json()
      except Exception as e:
        print(e)
        return False

      gov_data = next(iter(response), None)

      return gov_data

    def is_gov(self, host):
      if not host:
        return False

      gov_data = self.get_gov_data(host)

      if not gov_data:
        return False

      if gov_data['CC'] != 'TW':
        return False

      if gov_data['ASN'] != '4782':
        return False
        
      return True

if __name__ == '__main__':
    ip2gov = Ip2govAdapter()

    #host = '8.8.8.8'
    host = '61.57.37.60'
    print(ip2gov.is_gov(host))
