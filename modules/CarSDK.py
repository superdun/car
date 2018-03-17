# -*- coding: utf-8 -*-
import requests
import time
import hashlib


class CarOlineApi(object):
    def __init__(self, account, password):
        self.account = account
        self.password = password
        self.token = ""
        self.token_url = 'http://api.gpsoo.net/1/auth/access_token'
        self.monitor_url = 'http://api.gpsoo.net/1/account/monitor'
        self.tracking_url = 'http://api.gpsoo.net/1/devices/tracking'
        self.history_url = 'http://api.gpsoo.net/1/devices/history'
        self.address_url = 'http://api.gpsoo.net/1/tool/address'
        self.devinfo_url = 'http://api.gpsoo.net/1/account/devinfo'
        self.blacklist_url = 'http://api.gpsoo.net/1/tool/blacklist'

        self.map_type = 'BAIDU'
        self.paras = {"access_token": self.token, 'account': self.account, 'time': int(time.time())}
        self.hasToken = False

    def getSign(self, tm):
        md1 = hashlib.md5()
        md1.update(self.password)
        m1 = md1.hexdigest()
        md2 = hashlib.md5()
        md2.update(m1 + str(tm))
        m2 = md2.hexdigest()
        self.token = ""
        return m2

    def refrehToken(self, token):
        self.token = token
        self.paras['access_token']=token
        self.hasToken = True

    def payloadMaker(self, payload):
        newPayload = dict(self.paras.items() + payload.items())
        newPayload['time'] = int(time.time())
        return newPayload

    def getToken(self):
        tm = int(time.time())
        signature = self.getSign(tm)

        payload = {'account': self.account, 'time': tm, 'signature': signature}
        r = requests.get(self.token_url, params=payload)
        if 'access_token' in r.json():
            self.refrehToken(r.json()['access_token'])
        return self.token

    def monitor(self):
        if self.hasToken:
            payload = {'target': self.account, 'map_type': self.map_type}
            payload = self.payloadMaker(payload)
            r = requests.get(self.monitor_url, params=payload)
            return r.json()
        else:
            return {'err':'no token'}

    def tracking(self,ieis):
        if self.hasToken:
            payload = {'ieis': ieis, 'map_type': self.map_type}
            payload = self.payloadMaker(payload)
            r = requests.post(self.tracking_url, params=payload)
            return r.json()
        else:
            return {'err':'no token'}

    def history(self,imei,begin_time,end_time,limit=1000):
        if self.hasToken:
            payload = {'imei': imei, 'map_type': self.map_type,'begin_time':begin_time,'end_time':end_time,'limit':limit}
            payload = self.payloadMaker(payload)
            r = requests.get(self.history_url, params=payload)
            return r.json()
        else:
            return {'err':'no token'}

    def address(self,lng,lat):
        if self.hasToken:
            payload = {'lng': lng,'lat':lat, 'map_type': self.map_type}
            payload = self.payloadMaker(payload)
            r = requests.get(self.address_url, params=payload)
            return r.json()
        else:
            return {'err':'no token'}

    def devinfo(self):
        if self.hasToken:
            payload = {'target': self.account}
            payload = self.payloadMaker(payload)
            print payload
            r = requests.get(self.devinfo_url, params=payload)
            return r.json()
        else:
            return {'err':'no token'}

    def blacklist(self,cardno,drive_cardno):
        if self.hasToken:
            payload = {'cardno': cardno, 'drive_cardno': drive_cardno}
            payload = self.payloadMaker(payload)
            r = requests.get(self.blacklist_url, params=payload)
            return r.json()
        else:
            return {'err':'no token'}


# account = u'乐租'
# password = '12345663'
# car = CarOlineApi(account,password)
# car.getToken()
# print car.monitor()