# import class and constants
from ldap3 import Server, Connection, ALL

def is_anonymous_binding(host, port):
    try:
        s = Server(host=host, port=port, use_ssl=False, get_info='ALL', connect_timeout=10)
        c = Connection(s, auto_bind='NONE', version=3, authentication='ANONYMOUS', client_strategy='SYNC', auto_referrals=True, \
        check_names=True, read_only=False, lazy=False, raise_exceptions=False)

        r = c.bind()   # perform the Bind operation
        if not r:
            return False
            #print('error in bind', c.result)
    except Exception as e:
        print('error', e)
        return False
    #print(s.info)
    return True
    
#search_filter = '(objectclass=*)'
#r = c.search(search_base='dc=shini,dc=gov,dc=tw', search_filter=search_filter, search_scope='SUBTREE', attributes='*', paged_size = 5)
#print(r)
##
#print(c.entries)
if __name__  == '__main__':
    hosts = [
        '117.56.220.78', 
        '223.200.144.3',
        '223.200.98.38',
        '210.69.159.39',
    ]
    port = 389

    for host in hosts:
        r = is_anonymous_binding(host, port)
        print(host, r)
       
