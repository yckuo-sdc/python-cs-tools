#!/usr/bin/python3 
from package.request_adapter import RequestAdapter
from proxy.ssl_proxy_crawler import SslProxyCrawler
import os

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
