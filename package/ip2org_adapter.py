from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
import json
import os

class Ip2orgAdapter:   

    def __init__(self,  host=""): 
        if host == "":
            load_dotenv()
            self.host = os.getenv("IP2ORG_HOST")
        else:
            self.host = host 
            
    def get_org_data(self, host):
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
        
      org_data = dict()
      for index, value in enumerate(tds):
        key = ths[index].text
        value = value.text
        org_data[key] = value

      return org_data

    def is_org(self, host):
      org_data = self.get_org_data(host)
      if org_data['Country Code'] != 'TW':
        return False

      if org_data['ASN'] != '4782':
        return False
        
      return True

if __name__ == '__main__':
    ip2org = Ip2orgAdapter()

    #host = '8.8.8.8'
    host = '61.57.37.60'

    print(ip2org.is_org(host))
