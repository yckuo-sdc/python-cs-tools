import datetime
import json
import os
import re

import requests
from dotenv import load_dotenv

from bs4 import BeautifulSoup


class SslProxyCrawler:   
   def __init__(self):
       load_dotenv()
       self.proxy_host = os.getenv("SSL_PROXY_HOST")
       self.ip_check_host = os.getenv("IP_CHECK_HOST")
       self.export_filename = os.path.dirname(__file__) + '/proxy_list.json' 

   def is_valid(self, data):
       proxies = { "https" : data['proxy'] }
       print(proxies)
       try:
           response = requests.get(self.ip_check_host, proxies=proxies, timeout=5).json()
           if data['_proxy_ip'] == response['origin']:
               return True
       except Exception as e:
           print('{} invalid'.format(data['_proxy_ip']))
       return False

   def scrape_proxy_list(self):
       html_doc = requests.get(self.proxy_host)
       soup = BeautifulSoup(html_doc.text, 'html.parser')

       trs = soup.select("tbody tr")
       metas = []
       for tr in trs:
           tds = tr.select("td")
           if len(tds) > 6:
               ip = tds[0].text
               port = tds[1].text
               anonymity = tds[4].text
               scheme = 'https'
               proxy = scheme + '://' + ip + ':' + port
               proxy = ip + ':' + port
               if anonymity == 'anonymous':
                   meta = {
                   'port': port,
                   'proxy': proxy,
                   'dont_retry': True,
                   'download_timeout': 3,
                   '_proxy_scheme': scheme,
                   '_proxy_ip': ip
                   }
                   metas.append(meta)

       valid_metas = []
       for meta in metas:
           if self.is_valid(meta):
               valid_metas.append(meta)

       with open(self.export_filename, 'w') as f:
           json.dump(valid_metas, f)

   def get_valid_proxy_list(self):
       with open(self.export_filename) as f:
           proxies = json.load(f)

       valid_proxies = []
       #for proxy in proxies:
       #     if self.is_valid(proxy):
       #         valid_proxies.append(proxy)

       #updated_time = os.path.getmtime(self.export_filename)
       #updated_datetime = datetime.datetime.fromtimestamp(updated_time)
       #updated_at = updated_datetime.strftime("%Y-%m-%d %H:%M:%S")

       #return {'updated_at': updated_at, 'proxies': proxies}
       return proxies
       #return valid_proxies

if __name__  == '__main__':
    proxy = SslProxyCrawler()
    proxy.scrape_proxy_list()
    #print(proxy.get_valid_proxy_list())
