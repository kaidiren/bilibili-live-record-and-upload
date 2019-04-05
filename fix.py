import os
import sys
import commands

from flvlib.scripts import fix_flv
from flvlib.scripts import retimestamp_flv


filepath = ""
need_fix, offset = fix_flv.fix_flv(filepath, True)
if need_fix:
    os.rename(filepath, filepath + '.bak')
    copy(filepath+'.bak', filepath, offset)
    retimestamp_flv.retimestamp_file_inplace(filepath)