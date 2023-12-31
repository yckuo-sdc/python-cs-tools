#!/usr/bin/python3 
import os
import socket
import sys
from urllib.parse import urlparse


def is_opened(hostname, port):  
     try: 
        #print('ip: {}, port: {}'.format(hostname, port))
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

def get_service_info(data):
    service = {}
    if int(data['spt']) < int(data['dpt']):
        service['ip'] = data['src']
        service['port'] = data['spt']
    else:
        service['ip'] = data['dst']
        service['port'] = data['dpt']
    return service 

def get_ip_by_url(url):
    obj = urlparse(url)
    scheme = obj.scheme
    hostname = obj.hostname
    port = obj.port

    if scheme != 'http' and scheme != 'https': 
        return False
    if hostname is None:
        return False

    ip = socket.gethostbyname(hostname)
    return ip

if __name__ == '__main__':  
     #portList = [80, 443]  
     #hostname = 'web.yckuo.nics'
     #hostname = '10.33.26.1'

     #for port in portList:  
     #	print(is_opened(hostname, port)) 

     print(get_ip_by_url(hostname))
