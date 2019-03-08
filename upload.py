
import config
import time
from bilibiliupload import *

b = Bilibili()
b.login(config.username, config.password)
print('正在上传')
videos = [f for f in os.listdir('files') if f.endswith('.flv')]

tag = ['陈哥', '陈哥1', '直播', '录播']

desc = '陈哥404直播录播, 服务器自动录播自动投稿 喜欢的可以去关注陈哥1 https://live.bilibili.com/404'

for video in videos:
    filepath = os.path.abspath('./files/' + video)
    stat = os.stat(filepath)
    if stat.st_size <= 20 * 1024 * 1024:
        os.rename(filepath, filepath + '.skip')
        continue

    title = config.title_prefix + os.path.basename(filepath)[:-4]
    tid = 17
    b.upload(VideoPart(filepath), title, tid, tag, desc)
    os.rename(filepath, filepath + '.uploaded')
    print('上传成功', filepath)
    time.sleep(60)

