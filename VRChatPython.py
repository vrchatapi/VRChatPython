from urllib.request import urlopen, Request, urlretrieve
import urllib.request
import json
import base64

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib.request.install_opener(opener)

class VRChatPython(object):
    def __init__(self,username,password,api_url='https://api.vrchat.cloud/api/1'):
        self.api_key = None
        self.api_url = api_url
        self.base64auth = b'Basic ' + base64.b64encode(bytes(username + ':' + password, 'utf-8'))
        self.api_key = self.get_api_key()

    def json_convert(self,response):
        string = response.read().decode('utf-8')
        json_obj = json.loads(string)
        return json_obj

    def request_url(self,url,header_dat):
        header_dat['User-Agent'] = 'Mozilla/5.0'
        header_dat['Authorization'] = self.base64auth
        req = Request(url,headers=header_dat)
        response = urlopen(req)
        return response

    def make_request(self,url,params={},header_dat={}):
        if self.api_key != None:
            params['apiKey'] = self.api_key
        params_str = ''
        for param in params:
            if params_str == '':
                params_str += '?'
            else:
                params_str += '&'
            params_str += param + '=' + params[param]
        response = self.request_url(self.api_url + url + params_str,header_dat)
        json_response = self.json_convert(response)
        return json_response

    def get_api_key(self):
        config_response = self.make_request('/config')
        return config_response['clientApiKey']

    def save_image(self,url,file_name):
        urlretrieve(url,file_name)
