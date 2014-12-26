#!/usr/bin/env python
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from doubanfm.utils import Setting


os.system('echo \'%s\' | nc localhost %s' % (
    ' '.join(sys.argv[1:]), Setting.get('port')))
