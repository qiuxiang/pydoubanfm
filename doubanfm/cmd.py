import os
import sys
from .utils import setting


os.system('echo \'%s\' | nc localhost %s' % (
    ' '.join(sys.argv[1:]), setting.get('port')))
