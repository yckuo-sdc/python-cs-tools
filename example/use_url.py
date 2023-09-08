from helper.check_port_status import check_port_status
from helper.http_validator import *

# s1. check port stauts
# ip_list = [
#     '104.18.23.168',
#     '10.33.26.1',
#     '210.69.40.156',
# ]
# 
# port_list = [80, 443]  
# 
# for ip in ip_list:
#     for port in port_list:  
#         print(check_port_status(ip, port)) 

# s2. check url is reachable
url_list = [
    'https://stackoverflow.com',
    'http://web.yckuo.nics/phpmyadmin-nics',
    'http://web.yckuo.nics',
]

for url in url_list:
    print('{},  {}'.format(url, is_successful(url)))
