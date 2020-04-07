#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import re
from datetime import timedelta, datetime
import codecs

parser = argparse.ArgumentParser()
parser.add_argument('filename',
        help="input SRT file")
parser.add_argument('-d', '--delay', type=float, default=0.0,
        help="add delay in seconds")
parser.add_argument('-s', '--stretch', type=float, default=1.0,
        help="Stretch subtitles by factor s e.g. 1.001")
parser.add_argument('-t', '--transform', nargs=4,
        help="Stretch/shring/delay/advance. "
        "Provide 4 timestamps sub1 mov1 sub2 mov2 "
        "in the form HH:MM:SS[.mmm]. "
        "mov1 and sub1 shall match the same moment "
        "near the beggining of the movie and mov2 sub2 near the end. "
        "This overrides -s and -d. ")

args = parser.parse_args()

def parse_time_with_ms(a):
    try:
        t = datetime.strptime(a, '%H:%M:%S') 
    except ValueError:
        t = datetime.strptime(a, '%H:%M:%S.%f') 
    return t - datetime.strptime('00:00:00', '%H:%M:%S')

if args.transform:
    ts1 = parse_time_with_ms(args.transform[0])
    tm1 = parse_time_with_ms(args.transform[1])
    ts2 = parse_time_with_ms(args.transform[2])
    tm2 = parse_time_with_ms(args.transform[3])
    mov_diff = tm2 - tm1
    sub_diff = ts2 - ts1
    args.stretch = mov_diff / sub_diff
    s1 = ts1 * args.stretch
    args.delay = (tm1 - s1).total_seconds()
    print("Stretch = %f, delay=%f" % (args.stretch, args.delay),
            file=sys.stderr)

patt = re.compile(r'^(\d\d):(\d\d):(\d\d),(\d\d\d) --> '
        r'(\d\d):(\d\d):(\d\d),(\d\d\d)')

encodings = ['utf-8', 'cp1251', 'ascii']
for e in encodings:
    try:
        f = codecs.open(args.filename, 'r', encoding=e)
        f.readlines(20)
        f.seek(0)
    except UnicodeDecodeError:
        print("Bad codec %s" % e, file=sys.stderr)
    else:
        print("File opened with %s encoding" % e, file=sys.stderr)
        break

with f:
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
            t1 = timedelta(hours=h1, minutes=m1, seconds=s1, milliseconds=x1).total_seconds()
            t2 = timedelta(hours=h2, minutes=m2, seconds=s2, milliseconds=x2).total_seconds()
            y1 = t1 * args.stretch + args.delay
            y2 = t2 * args.stretch + args.delay
            h1, s1 = divmod(y1, 3600)
            m1, s1 = divmod(s1, 60)
            s1, x1 = divmod(s1, 1)
            h2, s2 = divmod(y2, 3600)
            m2, s2 = divmod(s2, 60)
            s2, x2 = divmod(s2, 1)
            print("{h1:02.0f}:{m1:02.0f}:{s1:02.0f},{x1:03.0f} --> "
                    "{h2:02.0f}:{m2:02.0f}:{s2:02.0f},{x2:03.0f}".format(
                h1=h1, m1=m1, s1=s1, x1=x1*1000, 
                h2=h2, m2=m2, s2=s2, x2=x2*1000))
        else:
            print(l, end='')

