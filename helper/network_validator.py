#!/usr/bin/python3 
from urllib.parse import urlparse
import socket  
import sys  
import os  

def is_opened(hostname, port):  
     try: 
        print('ip: {}, port: {}'.format(hostname, port))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)  # 2 seconds
        sock.connect((hostname,port))  
        return True
     except Exception as e:
        print(e)
        return False
     finally:
        sock.close()

def is_reachable(url):  
    obj = urlparse(url)
    scheme = obj.scheme
    hostname = obj.hostname
    port = obj.port

    if scheme != 'http' and scheme != 'https': 
        return False

    if hostname is None:
        return False

    if port is None: 
        if scheme == 'http':
            port = 80
        else:
            port = 443
    return is_opened(hostname, port)  

if __name__ == '__main__':  
     portList = [80, 443]  
     hostname = 'web.yckuo.nics'

     for port in portList:  
     	print(is_opened(hostname, port)) 