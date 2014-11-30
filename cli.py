#!/usr/bin/env python

import os
import sys
import json
import setting

os.system('echo \'%s\' | nc localhost %s' % (
    json.dumps(sys.argv[1:]), setting.get('port')))
