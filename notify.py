from Live import BiliBiliLive
import os, sys
import requests
import time
import config
import utils
import urllib3
urllib3.disable_warnings()


def inform(title):
    param = {
        'text': '陈哥开播啦~',
        'desp': title,
        'sendkey': config.sendkey
    }
    resp = requests.get(url=config.pushbear, params=param)
    print('通知完成！') if resp.status_code == 200 else None


class BiliBiliLiveRecorder(BiliBiliLive):
    def __init__(self, room_id):
        super().__init__(room_id)
        self.inform = inform
        self.print = utils.print_log
        self.room_title = None
        self.notify = True

    def check(self, interval):
        room_info = self.get_room_info()
        if room_info['status']:
            if self.notify:
                inform(room_info['roomname'])
                self.notify = False
        else:
            self.print(self.room_id, '等待开播')
            self.notify = True
        time.sleep(interval)

    def run(self):
        while True:
            self.check(interval=60)


b=BiliBiliLiveRecorder(404)
b.run()
