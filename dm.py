# -*- coding: utf-8 -*-
import base64
import hashlib
import logging
import math
import os
import re
import requests
import rsa
import time
import sys
import traceback

from io import BufferedReader
from typing import *
from urllib import parse

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class Bilibili:
    def __init__(self, cookie=None):
        self.session = requests.session()
        if cookie:
            self.session.headers["cookie"] = cookie
            self.csrf = re.search('bili_jct=(.*?);', cookie).group(1)
            self.mid = re.search('DedeUserID=(.*?);', cookie).group(1)
            self.session.headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
            self.session.headers['Referer'] = 'https://space.bilibili.com/{mid}/#!/'.format(mid=self.mid)

    def login(self, user, pwd):
        """

        :param user: username
        :type user: str
        :param pwd: password
        :type pwd: str
        :return: if success return True
                 else raise Exception
        """
        APPKEY    = '1d8b6e7d45233436'
        ACTIONKEY = 'appkey'
        BUILD     = 520001
        DEVICE    = 'android'
        MOBI_APP  = 'android'
        PLATFORM  = 'android'
        APPSECRET = '560c52ccd288fed045859ed18bffd973'

        def md5(s):
            h = hashlib.md5()
            h.update(s.encode('utf-8'))
            return h.hexdigest()

        def sign(s):
            """

            :return: return sign
            """
            return md5(s + APPSECRET)

        def signed_body(body):
            """

            :return: body which be added sign
            """
            if isinstance(body, str):
                return body + '&sign=' + sign(body)
            elif isinstance(body, dict):
                ls = []
                for k, v in body.items():
                    ls.append(k + '=' + v)
                body['sign'] = sign('&'.join(ls))
                return body

        def getkey():
            """

            :return: hash, key
            """
            r = self.session.post(
                    'https://passport.bilibili.com/api/oauth2/getKey',
                    signed_body({'appkey': APPKEY}),
            )
            json = r.json()
            data = json['data']
            return data['hash'], data['key']

        def cnn_captcha(img):
            url = "http://47.95.255.188:5000/code"
            data = {"image": img}
            r = requests.post(url, data=data)
            return r.text

        self.session.headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        h, k = getkey()
        pwd = base64.b64encode(
                  rsa.encrypt(
                      (h + pwd).encode('utf-8'),
                      rsa.PublicKey.load_pkcs1_openssl_pem(k.encode()),
                  ),
        )
        user = parse.quote_plus(user)
        pwd  = parse.quote_plus(pwd)

        r = self.session.post(
                'https://passport.bilibili.com/api/v2/oauth2/login',
                signed_body('appkey={appkey}&password={password}&username={username}'
                            .format(appkey=APPKEY, username=user, password=pwd)),
        )
        log.debug(r.text)
        json = r.json()

        if json['code'] == -105:
            # need captcha
            self.session.headers['cookie'] = 'sid=xxxxxxxx'
            r = self.session.get('https://passport.bilibili.com/captcha')
            captcha = cnn_captcha(base64.b64encode(r.content))
            r = self.session.post(
                    'https://passport.bilibili.com/api/v2/oauth2/login',
                    signed_body('actionKey={actionKey}&appkey={appkey}&build={build}&captcha={captcha}&device={device}'
                                '&mobi_app={mobi_app}&password={password}&platform={platform}&username={username}'
                                .format(actionKey=ACTIONKEY,
                                        appkey=APPKEY,
                                        build=BUILD,
                                        captcha=captcha,
                                        device=DEVICE,
                                        mobi_app=MOBI_APP,
                                        password=pwd,
                                        platform=PLATFORM,
                                        username=user)),
            )
            log.debug(r.text)
            json = r.json()

        if json['code'] != 0:
            raise Exception(r.text)

        cookie = '; '.join(
            '%s=%s' % (item['name'], item['value'])
            for item in json['data']['cookie_info']['cookies']
        )
        self.session.headers["cookie"] = cookie
        self.csrf = re.search('bili_jct=(.*?);', cookie).group(1)
        self.mid = re.search('DedeUserID=(.*?);', cookie).group(1)
        self.session.headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
        self.session.headers['Referer'] = 'https://space.bilibili.com/{mid}/#!/'.format(mid=self.mid)

        return True

    def danmaku_post(self, aid, cid, message, page=1, moment=-1):
        # aid = 稿件av号
        # message = 弹幕内容
        # page = 分P
        # moment = 弹幕发送时间
        url = "https://api.bilibili.com/x/v2/dm/post"
        headers = {
            'Host': "api.bilibili.com",
            'Origin': "https://www.bilibili.com",
            'Referer': f"https://www.bilibili.com/video/av{aid}",
        }
        payload = {
                'type': 1,
                'oid': cid,
                'msg': message,
                'aid': aid,
                'progress': int(moment * 1E3) if moment != -1 else random.randint(0, duration * 1E3),
                'color': 16777215,
                'fontsize': 25,
                'pool': 0,
                'mode': 1,
                'rnd': int(time.time() * 1E6),
                'plat': 1,
                'csrf': self.csrf,
                }
        r = self.session.post(url, data=payload, headers=headers)
        json = r.json()
        print(r.text)

if __name__ == '__main__':
    b = Bilibili()
    b.login('13116639741', 'kk12345')

    f = open('a')
    for line in f.readlines():
        line = line.strip().split(',')
        page = int(line[0])
        aid = int(line[1])
        cid = int(line[2])
        ts = int(line[3])
        dm = line[4]
        print(line)
        try:
            b.danmaku_post(aid, cid, dm, page, ts)
        except Exception as e:
            logging.error(traceback.format_exc())
        time.sleep(15)
    f.close()
    sys.exit()
