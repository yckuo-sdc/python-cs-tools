import requests
import configparser
import csv
import os

class VirusTotal:   
   def __init__(self,host="",apikey=""):
       if host == "" or apikey == "":
         config = configparser.ConfigParser()
         config.read('config.ini', encoding='utf-8')
         self.host = config['virustotal']['host']
         self.apikey = config['virustotal']['apikey']
       else:
         self.host=host
         self.apikey=apikey

   def scan_url(self, target_url):
     url = self.host + "/urls"
     payload = { "url": target_url }
     headers = {
         "accept": "application/json",
         "x-apikey": self.apikey,
         "content-type": "application/x-www-form-urlencoded",
     }
     
     j = requests.post(url, data=payload, headers=headers).json()

     try:
       j['data']['id']
     except:
       print("well, wet don't get report id!")
       vid = False
     else:
       vid = j['data']['id']
     finally:
       return vid;

   def get_scan_report(self, vid):
     url = self.host + "/analyses/" + vid
     headers = {
         "accept": "application/json",
         "x-apikey": self.apikey,
     }
     
     j = requests.get(url, headers=headers).json()
      
     return j['data']['attributes']['stats']



if __name__  == '__main__':
  vt = VirusTotal()

  with open(os.path.dirname(__file__) + '/../data/malicious.csv', newline='') as csvfile:
  
    rows = csv.reader(csvfile)
    next(rows, None)  # skip the headers
  
    for index, row in enumerate(rows):
      for url in row:
        print(str(index+1) + ': ' + url)
        vid = vt.scan_url(url)
        if vid:
          stats = vt.get_scan_report(vid)
          print(stats)
