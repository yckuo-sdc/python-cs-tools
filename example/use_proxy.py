#!/usr/bin/python3 
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'package'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'proxy'))

from request_adapter import RequestAdapter
from ssl_proxy_crawler import SslProxyCrawler

proxy = SslProxyCrawler()
valid_proxy_list = proxy.get_valid_proxy_list()
proxy = next(iter(valid_proxy_list), None)

if not proxy:
    print('no valid proxies')
    os._exit(0)

proxies = {'https': proxy['proxy']}
print(proxies)

ra = RequestAdapter(proxies=proxies)

r = ra.get("https://httpbin.org/ip", headers={"Accept": "application/json"}, timeout=5)
print(r.request.headers)
print(r.text)
