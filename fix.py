# -*- coding: UTF-8 -*-
import os
import sys
import commands

from flvlib.scripts import fix_flv
from flvlib.scripts import retimestamp_flv


def copy(src,dest,length,bufsize=10*1024*1024):
    with open(src,'rb') as fout:
        fout.seek(0)
        with open(dest,'wb') as fin:
            while length:
                chunk = min(bufsize,length)
                data = fout.read(chunk)
                fin.write(data)
                length -= chunk

filepath = "/Users/rkd/Desktop/bili/20190422_2021_非洲地牢.运气不够技术凑.flv"
need_fix, offset = fix_flv.fix_flv(filepath, True)
if need_fix:
    os.rename(filepath, filepath + '.bak')
    copy(filepath+'.bak', filepath, offset)
    retimestamp_flv.retimestamp_file_inplace(filepath)
