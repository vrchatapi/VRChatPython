import requests

class Call:
    def __init__(self):
        self.apiKey = None
        self.b64_auth = None

    def set_auth(self, b64_auth):
        # Assume good b64_auth
        self.b64_auth = b64_auth

    def call(self, path, method="GET", headers={}, params={}, no_auth=False):
        headers["user-agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",

        if no_auth:
            return self._call(path, method, headers, params)

        if self.b64_auth == None:
            raise Exception("Tried to do authenticated request without setting b64 auth (Call.set_auth(b64_auth))!")
        headers["Authorization"] = "Basic "+self.b64_auth

        if self.apiKey == None:
            resp = requests.get("https://api.vrchat.cloud/api/1/config")
            assert resp.status_code == 200

            j = resp.json()
            try:
                self.apiKey = j["apiKey"]
            except:
                raise Exception("This API wrapper is too outdated to function (https://api.vrchat.cloud/api/1/config doesn't contain apiKey)")

        path = "https://api.vrchat.cloud/api/1" + path + "?apiKey=" + self.apiKey
        resp = requests.request(method, path, headers=headers, params=params)

        if resp.status_code != 200:
            try: json = resp.json()
            except: json = None

            return {"status": resp.status_code, "data": json if json not None else resp.content}

        return {"status": resp.status_code, "data": resp.json()}

    def _call(self, path, method="GET", headers={}, params={}):
        if self.apiKey == None:
            resp = requests.get("https://api.vrchat.cloud/api/1/config")
            assert resp.status_code == 200

            j = resp.json()
            try:
                self.apiKey = j["apiKey"]
            except:
                raise Exception("This API wrapper is too outdated to function (https://api.vrchat.cloud/api/1/config doesn't contain apiKey)")

        path = "https://api.vrchat.cloud/api/1" + path + "?apiKey=" + self.apiKey
        resp = requests.request(method, path, headers=headers, params=params)

        if resp.status_code != 200:
            try: json = resp.json()
            except: json = None

            return {"status": resp.status_code, "data": json if json not None else resp.content}

        return {"status": resp.status_code, "data": resp.json()}
