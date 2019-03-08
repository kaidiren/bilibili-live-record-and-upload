from Live import BiliBiliLive
import os, sys
import requests
import time
import config
import utils
import multiprocessing
import urllib3
from bilibiliupload import *
urllib3.disable_warnings()

import atexit

class BiliBiliLiveRecorder(BiliBiliLive):
    def __init__(self, room_id):
        super().__init__(room_id)
        self.inform = utils.inform
        self.print = utils.print_log
        self.room_title = None

    def check(self, interval):
        while True:
            room_info = self.get_room_info()
            if room_info['status']:
                self.inform(room_id=self.room_id,desp=room_info['roomname'])
                self.print(self.room_id, room_info['roomname'])
                self.room_title = room_info['roomname']
                break
            else:
                self.print(self.room_id, '等待开播')
            time.sleep(interval)
        return self.get_live_urls()

    def record(self, record_url, output_filename):
        self.print(self.room_id, '√ 正在录制...' + self.room_id)
        resp = requests.get(record_url, stream=True)
        with open(output_filename, "wb") as f:
            for chunk in resp.iter_content(chunk_size=512):
                f.write(chunk) if chunk else None

    def run(self):
        while True:
            urls = self.check(interval=60)
            filename = utils.generate_filename(self.room_id)
            filename =  filename.split('.flv')
            filename = filename[0]
            filename = filename.split('_')
            filename.pop()
            filename.append(self.room_title)
            filename = '_'.join(filename) + '.flv'
            c_filename = os.path.join(os.getcwd(), 'files', filename)
            self.record(urls[0], c_filename)
            self.print(self.room_id, '录制完成')
            self.upload(c_filename)
    def upload(self, filepath):
        b = Bilibili()
        b.login(config.username, config.password)
        print('正在上传', filepath)

        tag = ['陈哥', '陈哥1', '直播', '录播']

        desc = '陈哥404直播录播, 服务器自动录播自动投稿 喜欢的可以去关注陈哥1 https://live.bilibili.com/404'

        stat = os.stat(filepath)
        if stat.st_size <= 20 * 1024 * 1024:
            os.rename(filepath, filepath + '.skip')
            return

        title = config.title_prefix + os.path.basename(filepath)[:-4]
        tid = 17
        
        b.upload(VideoPart(filepath), title, tid, tag, desc)
        os.rename(filepath, filepath + '.uploaded')
        
        time.sleep(60)

        print('上传成功', filepath)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        input_id = [str(sys.argv[1])]
    elif len(sys.argv) == 1:
        input_id = config.rooms  # input_id = '917766' '1075'
    else:
        raise ZeroDivisionError('请检查输入的命令是否正确 例如：python3 run.py 10086')

    mp = multiprocessing.Process
    tasks = [mp(target=BiliBiliLiveRecorder(room_id).run) for room_id in input_id]
    for i in tasks:
        i.start()
    for i in tasks:
        i.join()
