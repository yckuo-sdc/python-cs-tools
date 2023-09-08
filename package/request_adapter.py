import requests


class RequestAdapter:
    def __init__(self, **kwargs):
        self.session = requests.Session()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'} 
        self.session.headers.update(headers)

        #if proxies:
        #    self.session.headers.update(headers)

        for arg in kwargs:
            if isinstance(kwargs[arg], dict):
                kwargs[arg] = self.__deep_merge(getattr(self.session, arg), kwargs[arg])
            setattr(self.session, arg, kwargs[arg])

    def request(self, method, url, **kwargs):
        try:
            return self.session.request(method, url, **kwargs)
        except Exception as e:
            print(e)

    def head(self, url, **kwargs):
        try:
            return self.session.head(url, **kwargs)
        except Exception as e:
            print(e)

    def get(self, url, **kwargs):
        try:
            return self.session.get(url, **kwargs)
        except Exception as e:
            print(e)

    def post(self, url, **kwargs):
        try:
            return self.session.post(url, **kwargs)
        except Exception as e:
            print(e)

    def put(self, url, **kwargs):
        try:
            return self.session.put(url, **kwargs)
        except Exception as e:
            print(e)

    def patch(self, url, **kwargs):
        try:
            return self.session.patch(url, **kwargs)
        except Exception as e:
            print(e)

    def delete(self, url, **kwargs):
        try:
            return self.session.delete(url, **kwargs)
        except Exception as e:
            print(e)

    @staticmethod
    def __deep_merge(source, destination):
        for key, value in source.items():
            if isinstance(value, dict):
                node = destination.setdefault(key, {})
                RequestsApi.__deep_merge(value, node)
            else:
                destination[key] = value
        return destination

if __name__ == '__main__':
    proxies = {'https': '186.121.235.222:8080'}
    ra = RequestAdapter(enable_proxies=True)
    #ra = RequestAdapter()
    r = ra.get("https://httpbin.org/ip", headers={"Accept": "application/json"}, timeout=5)
    print(r.request.headers)
    print(r.text)

