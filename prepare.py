 # -*- coding: utf-8 -*-

import config
import time
import os
import sys
import commands

from flvlib.scripts import fix_flv
from flvlib.scripts import retimestamp_flv

if os.path.isfile('files/.recording'):
    sys.exit()


def copy(src,dest,length,bufsize=10*1024*1024):
    with open(src,'rb') as fout:
        fout.seek(0)
        with open(dest,'wb') as fin:
            while length:
                chunk = min(bufsize,length)
                data = fout.read(chunk)
                fin.write(data)
                length -= chunk


def concat(files):
    new_file_name = files[0] + '.new.flv'
    os.remove('files/inputs.txt') if os.path.exists('files/inputs.txt') else None
    inputs = []
    for file in files:
        inputs.append("file '{}'".format(file))
    inputs = '\n'.join(inputs)
    print(inputs)
    f = open('files/inputs.txt', 'w')
    f.write(inputs)
    f.close()


    print("ffmpeg -f concat -safe 0 -i files/inputs.txt -c copy {} -y".format(new_file_name))
    _, text = commands.getstatusoutput("ffmpeg -f concat -safe 0 -i files/inputs.txt -c copy {} -y".format(new_file_name))
    text = text.split('\n')
    for line in text:
        print(line)
        # if "Duration:" in line:
        #     print(line[12:23])

    for file in files:
        os.rename(file, file + '.merged')

    os.rename(new_file_name, new_file_name[:-8])
    os.remove('files/inputs.txt') if os.path.exists('files/inputs.txt') else None

videos = [f for f in os.listdir('files') if f.endswith('.flv')]
videos.sort()


for video in videos:
    filepath = os.path.abspath('./files/' + video)
    need_fix, offset = fix_flv.fix_flv(filepath, True)
    if need_fix:
        os.rename(filepath, filepath + '.bak')
        copy(filepath+'.bak', filepath, offset)
        retimestamp_flv.retimestamp_file_inplace(filepath)


videos = [f for f in os.listdir('files') if f.endswith('.flv')]
videos.sort()

files = []
last_file_name = ''
for video in videos:
    filepath = os.path.abspath('./files/' + video)
    current_file_name = video[14:]
    if last_file_name == '':
        last_file_name = current_file_name
        files.append(filepath)
    elif last_file_name == current_file_name:
        files.append(filepath)
    elif last_file_name != current_file_name:
        # do files
        if len(files) > 1:
            concat(files)
        files = []
        files.append(filepath)
        last_file_name = current_file_name

    code, text=commands.getstatusoutput("ffmpeg -i {}".format(filepath))
    text = text.split('\n')
    for line in text:
        if "Duration:" in line:
            print(current_file_name)
            print(line[12:23])

if len(files) > 1:
    concat(files)

time.sleep(120)
