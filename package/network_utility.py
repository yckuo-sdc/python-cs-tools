#!/usr/bin/python3 
from urllib.parse import urlparse
import socket  
import sys  
import os  

class NetworkUtility: 

    def __init__(self,  url=""): 
        obj = urlparse(url)
        #print(obj)
        self.scheme = obj.scheme
        self.hostname = obj.hostname
        self.port = obj.port
        self.netloc = obj.netloc

    def is_opened(self):  
         try: 
            #print('ip: {}, port: {}'.format(self.hostname, self.port))
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)  # 5 seconds
            sock.connect((self.hostname, self.port))  
            return True
         except Exception as e:
            print(e)
            return False
         finally:
            sock.close()

    def is_reachable(self):  
        if self.scheme != 'http' and self.scheme != 'https': 
            return False

        if self.hostname is None:
            return False

        if self.port is None: 
            if self.scheme == 'http':
                self.port = 80
            else:
                self.port = 443
        return self.is_opened()  

    def get_ip(self):
        if self.scheme != 'http' and self.scheme != 'https': 
            return False
        if self.hostname is None:
            return False

        try: 
            #socket.setdefaulttimeout(5) # 5 seconds
            ip = socket.gethostbyname(self.hostname)
        except Exception as e:
            print(e)
            return False
        return ip

    def get_netloc(self):
        return self.scheme + '://' + self.netloc

if __name__ == '__main__':  

     url = 'http://220.130.190.61'
     url = 'http://web.yckuo.nics'
     net_utl = NetworkUtility(url)

     print(net_utl.get_ip())
     print(net_utl.get_netloc())
