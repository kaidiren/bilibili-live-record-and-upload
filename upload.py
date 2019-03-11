
import config
import time
import os
from bilibiliupload import *

b = Bilibili()
b.login(config.username, config.password)

videos = [f for f in os.listdir('files') if f.endswith('.flv')]

tag = ['陈哥', '陈哥1', '直播', '录播']

desc = '[已授权]陈哥404直播录播, 服务器自动录播自动投稿，仅用于回看，请勿商业使用 喜欢的可以去关注陈哥1 https://live.bilibili.com/404 \n 说明：服务器每天实时录制，在凌晨2点定时上传(一家之主可能熬夜)，审稿需要一定时间（2-6小时）请耐心等待，如果一切顺利中午12点前应该可以看到 \n 文件大小达到 4 GB 会自动分割（文件过大容易上传失败），请根据标题里的时间自行翻阅'

for video in videos:
    print('正在上传', video)
    filepath = os.path.abspath('./files/' + video)
    stat = os.stat(filepath)
    if stat.st_size <= 20 * 1024 * 1024:
        os.rename(filepath, filepath + '.skip')
        continue
    if time.time() - stat.st_mtime <= 60 * 10:
        continue

    title = config.title_prefix + os.path.basename(filepath)[:-4]
    tid = 17
    b.upload(VideoPart(filepath), title, tid, tag, desc)
    os.rename(filepath, filepath + '.uploaded')
    print('上传成功', filepath)
    time.sleep(60)

videos = [f for f in os.listdir('files') if f.endswith('.uploaded')]

for video in videos:
    filepath = os.path.abspath('./files/' + video)
    stat = os.stat(filepath)
    if time.time() - stat.st_mtime >= 3600 * 24 * 5:
        os.remove(filepath)
        print(filepath, 'deleted')