import config
import time
import os
import sys
import requests
import shutil
import traceback
import logging
import subprocess

from datetime import datetime, timedelta

from bilibiliupload import Bilibili, VideoPart

if os.path.isfile('files/.recording'):
    print('.recording exists')
    sys.exit()

delta = 1
for arg in sys.argv:
    if arg == '-t':
        delta = 0

yesterday = datetime.strftime(datetime.now() - timedelta(delta), '%Y%m%d')
sub_dir = 'files/' + yesterday + '/'

if not os.path.exists(sub_dir):
    print(sub_dir + ' not exists')
    sys.exit()
if os.path.isfile(sub_dir + '.uploaded'):
    print('.uploaded file exists')
    sys.exit()


if os.path.isfile(sub_dir + '.uploading'):
    if time.time() - os.stat(sub_dir + '.uploading').st_mtime > 3600 * 4:
        requests.get(url=config.pushbear, params={
            'text': '上传可能出BUG了',
            'desp': '上传可能出BUG了',
            'sendkey': config.sendkey
        })
    sys.exit()

open(sub_dir + '.uploading', 'a').close()

desc = '[已授权]陈哥404直播录播,仅用于回看,请勿商业使用 请关注陈哥直播间 https://live.bilibili.com/404\n服务器每天自动录制,自动投稿,自动分P,凌晨2点定时上传,审稿需要6-12小时请耐心等待\n本录播不做整理,不录弹幕,催更毫无意义,谢谢~'

videos = [f for f in os.listdir(sub_dir) if f.endswith('.flv')]
videos.sort()

for video in videos:
    filepath = os.path.abspath(sub_dir + video)
    code, text = subprocess.getstatusoutput("ffmpeg -i {} -vcodec copy -acodec copy {}.mp4 -y ".format(filepath, filepath[:-4]))
    print(filepath)
    print(code)
    print(text)
    os.rename(filepath, filepath + '.bak')

videos = [f for f in os.listdir(sub_dir) if f.endswith('.mp4')]
videos.sort()

if not len(videos):
    print('no living yesterday: ' + sub_dir)
    os.remove(sub_dir + '.uploading') if os.path.exists(sub_dir + '.uploading') else None
    sys.exit()

tag = ['陈哥404直播录播', '无情服务器录播', '404录播姬']
parts = []
for video in videos:
    filepath = os.path.abspath(sub_dir + video)
    title = '['+video[9:11] + ':'+video[11:13] + ']' + video[14:-4]
    if video[:8] != yesterday:
        title = '[深夜]' + title
    print(filepath, title)
    parts.append(VideoPart(filepath, title))

print('正在上传 ' + sub_dir)
title = '[' + yesterday + ']' + parts[0].title[7:]
tid = 17
b = Bilibili()
b.login(config.username, config.password)
try:
    b.upload(parts, title, tid, tag, desc)
except Exception as e:
    logging.error(traceback.format_exc())
    os.remove(sub_dir + '.uploading') if os.path.exists(sub_dir + '.uploading') else None
    sys.exit()


open(sub_dir + '.uploaded', 'a').close()

for video in videos:
    filepath = os.path.abspath(sub_dir + video)
    os.rename(filepath, filepath + '.uploaded')


dirs = [f for f in os.listdir('files') if os.path.isdir('files/' + f)]
dirs.sort()

for dir in dirs:
    dirpath = os.path.abspath('files/' + dir)
    stat = os.stat(dirpath)
    if time.time() - stat.st_mtime >= 3600 * 24 * 13:
        shutil.rmtree(dirpath)
        print(dirpath, 'deleted')

os.remove(sub_dir + '.uploading') if os.path.exists(sub_dir + '.uploading') else None
