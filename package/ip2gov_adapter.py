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
      url = self.host + "/result"
      payload = { "IP": host, "OID": ""}
      headers = {
          "content-type": "application/x-www-form-urlencoded",
      }

      response = requests.post(url, data=payload, headers=headers)
      html_doc = response.text
      soup = BeautifulSoup(html_doc, 'html.parser')
      ths = soup.find_all('th')
      tds = soup.find_all('td')
        
      gov_data = dict()
      for index, value in enumerate(tds):
        key = ths[index].text
        value = value.text
        gov_data[key] = value

      return gov_data

    def is_gov(self, host):
      if not host:
        return False

      gov_data = self.get_gov_data(host)
      if gov_data['Country Code'] != 'TW':
        return False

      if gov_data['ASN'] != '4782':
        return False
        
      return True

if __name__ == '__main__':
    ip2gov = Ip2govAdapter()

    #host = '8.8.8.8'
    host = '61.57.37.60'

    print(ip2gov.is_gov(host))
