#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import re
from datetime import timedelta, datetime

parser = argparse.ArgumentParser()
parser.add_argument('filename',
        help="input SRT file")
parser.add_argument('-d', '--delay', type=float, default=0.0,
        help="add delay in seconds")
parser.add_argument('-s', '--stretch', type=float, default=1.0,
        help="Stretch subtitles by factor s e.g. 1.001")
parser.add_argument('-t', '--transform', nargs=2,
        help="Transform HH:MM:SS -> HH:MM:SS. Overrides -s")
args = parser.parse_args()

if args.transform:
    td1 = (datetime.strptime(args.transform[0], '%H:%M:%S') -
            datetime.strptime('00:00:00', '%H:%M:%S'))
    td2 = (datetime.strptime(args.transform[1], '%H:%M:%S') -
            datetime.strptime('00:00:00', '%H:%M:%S'))
    args.stretch = td2 / td1

patt = re.compile(r'^(\d\d):(\d\d):(\d\d),(\d\d\d) --> '
        r'(\d\d):(\d\d):(\d\d),(\d\d\d)')

with open(args.filename, encoding='cp1251') as f:
    for l in f:
        m = patt.search(l)
        if m:
            h1 = int(m.group(1))
            m1 = int(m.group(2))
            s1 = int(m.group(3))
            x1 = int(m.group(4))
            h2 = int(m.group(5))
            m2 = int(m.group(6))
            s2 = int(m.group(7))
            x2 = int(m.group(8))
            t1 = timedelta(hours=h1, minutes=m1, seconds=s1, milliseconds=x1)
            t2 = timedelta(hours=h2, minutes=m2, seconds=s2, milliseconds=x2)
            y1 = t1 * args.stretch + timedelta(seconds=args.delay)
            y2 = t2 * args.stretch + timedelta(seconds=args.delay)
            s1 = y1.seconds + y1.microseconds / 1e6
            s2 = y2.seconds + y1.microseconds / 1e6
            h1, s1 = divmod(s1, 3600)
            m1, s1 = divmod(s1, 60)
            s1, x1 = divmod(s1, 1)
            h2, s2 = divmod(s2, 3600)
            m2, s2 = divmod(s2, 60)
            s2, x2 = divmod(s2, 1)
            print("{h1:02.0f}:{m1:02.0f}:{s1:02.0f},{x1:03.0f} --> "
                    "{h2:02.0f}:{m2:02.0f}:{s2:02.0f},{x2:03.0f}".format(
                h1=h1, m1=m1, s1=s1, x1=x1*1000, 
                h2=h2, m2=m2, s2=s2, x2=x2*1000))
        else:
            print(l, end='')

