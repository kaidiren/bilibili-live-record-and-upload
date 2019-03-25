import config
import time
import os
import sys
import requests
import subprocess
import math

from bilibiliupload import Bilibili, VideoPart

if os.path.isfile('files/.uploading'):
    if time.time() - os.stat('files/.uploading').st_mtime > 3600 * 4:
        requests.get(url=config.pushbear, params={
            'text': '上传可能出BUG了',
            'desp': '上传可能出BUG了',
            'sendkey': config.sendkey
        })
    sys.exit()

open('files/.uploading', 'a').close()

b = Bilibili()
b.login(config.username, config.password)

videos = [f for f in os.listdir('files') if f.endswith('.flv')]
videos.sort()

desc = '[已授权]陈哥404直播录播, 服务器自动录播自动投稿，仅用于回看，请勿商业使用 喜欢的可以去关注陈哥1 https://live.bilibili.com/404 \n 喜欢看整理过的录播可以去 咲茗奇 空间 11693477  \n 说明：服务器每天实时录制，在凌晨2点定时上传(一家之主可能熬夜)，审稿需要一定时间（2-6小时）请耐心等待，如果一切顺利中午12点前应该可以看到 \n 文件大小达到 4 GB 会自动分割（文件过大容易上传失败），请根据标题里的时间自行翻阅'

for video in videos:
    tag = ['陈哥404直播录播', '无情服务器录播', '404录播姬']
    filepath = os.path.abspath('./files/' + video)
    stat = os.stat(filepath)
    parts = VideoPart(filepath)
    if stat.st_size <= 200 * 1024 * 1024:
        os.rename(filepath, filepath + '.skip')
        continue
    if time.time() - stat.st_mtime <= 5 * 60:
        continue
    if stat.st_size >= 8 * 1000 * 1000 * 1000:
        code, text=subprocess.getstatusoutput("ffmpeg -i {}".format(filepath))
        text = text.split('\n')
        duration = ''
        for line in text:
            if "Duration:" in line:
                duration = line[12:23]

        if duration != '':
            duration = duration.split(':')
            hour = math.ceil((int(duration[0]) * 60 + int(duration[1])) / 2.0 / 60.0)
            hour = int(hour)
            p1 = 'ffmpeg -i {} -ss 00:00:00 -t 0{}:00:00 -vcodec copy -acodec copy {}.p1.flv -y'.format(filepath, hour, filepath)
            p2 = 'ffmpeg -i {} -ss 0{}:00:00 -vcodec copy -acodec copy {}.p2.flv -y'.format(filepath, hour, filepath)
            subprocess.getstatusoutput(p1)
            subprocess.getstatusoutput(p2)
            parts = [VideoPart(filepath + '.p1.flv', 'P1'), VideoPart(filepath+ '.p2.flv', 'P2')]
    print('正在上传', video)
    name = os.path.basename(filepath)
    title = '[' + name[:8] + ']' + '['+name[9:11] + ':'+name[11:13] + ']' + name[14:-4]
    tid = 17
    b.upload(parts, title, tid, tag, desc)
    os.rename(filepath, filepath + '.uploaded')
    print('上传成功', filepath)
    time.sleep(60)

videos = [f for f in os.listdir('files') if f.endswith('.uploaded') or f.endswith('.bak') or f.endswith('.merged')]
videos.sort()

for video in videos:
    filepath = os.path.abspath('./files/' + video)
    stat = os.stat(filepath)
    if time.time() - stat.st_mtime >= 3600 * 24 * 7:
        os.remove(filepath)
        print(filepath, 'deleted')

os.remove('files/.uploading')
