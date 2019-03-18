#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Dumps user form CloudiFest App
# You need CloudFest app installed on rooted android
# After registered the App and get list of users, copy the database using:
# adb pull /data/data/com.xailabs.whd/databases/rocketchat /tmp
# you need adb root access to do this.

import sqlite3
import json

conn = sqlite3.connect('/tmp/rocketchat')
c = conn.cursor()

headers = []
lines = []
for row in c.execute("SELECT json FROM RestUser"):
    try:
        j = json.loads(row[0])
        cf = j['customFields']
        for k,v in cf.items():
            if k not in headers:
                headers.append(k)
        lines.append(cf)
    except ValueError:
        pass

headers.sort()
print(",".join(headers))
for row in lines:
    r = ['"%s"' % row.get(x, '') for x in headers]
    print(",".join(r))
