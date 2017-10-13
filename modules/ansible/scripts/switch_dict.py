# -*- coding: utf-8 -*-
import json
import sys

key = sys.argv[1]
with open(key, 'r') as f:
    data = f.read()

bb = json.loads(data)
cc = bb['records']
for dd in cc:
    type = dd['type']
    name = dd['name'] + '.' + key
    value = dd['value']
    status = dd['status']
    line = dd['line']

    msg = "%s,%s,%s,%s,%s\n" % (name, type, value, status, line)
    out = key + '.log'
    with open(out, 'a+') as f:
        f.write(msg)
