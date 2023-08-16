from dotenv import load_dotenv
import requests
import csv
import os

class VirusTotal:   
   def __init__(self,host="",apikey=""):
       if host == "" or apikey == "":
         load_dotenv()
         self.host = os.getenv("VT_HOST")
         self.apikey = os.getenv("VT_APIKEY")
       else:
         self.host=host
         self.apikey=apikey

   def get_ip_report(self, ip): 
     url = self.host + "/ip_addresses/" + ip
     headers = {
         "accept": "application/json",
         "x-apikey": self.apikey,
     }
     j = requests.get(url, headers=headers).json()
     return j

   def get_file_report(self, filehash): 
     url = self.host + "/files/" + filehash
     headers = {
         "accept": "application/json",
         "x-apikey": self.apikey,
     }
     j = requests.get(url, headers=headers).json()

     if 'error' in j:
        return None

     return j['data']['attributes']['last_analysis_stats']

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

   def is_malicious_by_filehash(self, filehash):
     if not filehash:
        return False

     stats = self.get_file_report(filehash)

     if not stats:
       return False
     
     malicious_number = stats['malicious']

     if malicious_number:
        return True

     return False

   
   def is_malicious_by_url(self, target_url):
    vid = self.scan_url(target_url)
    response = False

    if not vid:
        return False

    stats = self.get_scan_report(vid)
    malicious_number = stats['malicious'] + stats['suspicious']  
    if malicious_number:
        return True

    return False

      

if __name__  == '__main__':

  vt = VirusTotal()

  filehash = "51340B563B779603DB13861B0978537FCDC00341"
  filehash = "139933FDC6163334F161D85F015CE81F73803C95"
  print(vt.is_malicious_by_filehash(filehash))


  #url_list = [
  #  'http://220.130.190.61'
  #]

  #for url in url_list:
  #  print('url: {}, malicious: {}'.format(url, vt.is_malicious(url)))

  # ip = '211.73.81.111'
  # response = vt.get_ip_report(ip)
  # print(response)

  #with open(os.path.dirname(__file__) + '/../data/malicious.csv', newline='') as csvfile:
  #
  #  rows = csv.reader(csvfile)
  #  next(rows, None)  # skip the headers
  #
  #  for index, row in enumerate(rows):
  #    for url in row:
  #      print(str(index+1) + ': ' + url)
  #      vid = vt.scan_url(url)
  #      if vid:
  #        stats = vt.get_scan_report(vid)
  #        print(stats)
