from dotenv import load_dotenv
import requests
import csv
import os
import re

class BoturlValidator:   
   def __init__(self):
       self.host = ""

   def pass_request_payload_test(self, url, shell_pwd): 
       test_commands = {
           "php": "system('whoami');",
           "asp": "Server.Execute('whoami')",
           "jsp": "Runtime rt = Runtime.getRuntime(); rt.exec('whoami');",
       }
       
       headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'}

       for test_cmd in test_commands.values():
           payload = {shell_pwd: test_cmd}
           r = requests.post(url, data=payload, headers=headers, allow_redirects=False, timeout=10)
           print(r.request.headers)
           print(r.request.body)

           if len(r.content) > 0:
                print(r.text)
                return True

       return False

   def fetch_shell_password(self, boturl): 
       if not boturl:
           return False

       pattern = '^\w*?(?=%3D)'
       result = re.search(pattern, boturl)
       if not result:
           return False
       
       return result.group() 

   def is_malicious_by_boturl(self, url, boturl): 
       shell_pwd = self.fetch_shell_password(boturl)

       if not shell_pwd:
           return False

       return self.pass_request_payload_test(url, shell_pwd)

if __name__  == '__main__':

   bt = BoturlValidator()
   url = "http://web.yckuo.nics/hackable/test.php"
   boturl = "mytestshell%3Daabbcc"
 
   print(url, boturl)

   r = bt.is_malicious_by_boturl(url, boturl)
   print(r)
