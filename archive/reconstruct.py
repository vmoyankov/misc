#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import os
import sys
import fnmatch
import os.path
from pathlib import Path
import re

# globals
args = None
index = {}
translate = []


def match_filter(path):

    if not args.filter:
        return True

    for f in args.filter:
        if fnmatch.fnmatch(path, f):
            return True

    return False


def load_index(index_filename):

    global index
    global translate

    with open(index_filename) as index_file:
        reader = csv.reader(index_file)
        for row in reader:
            hash, mtime, size, path = row[:]
            if not match_filter(path):
                continue

            # translate path
            for search, replace in translate:
                path = re.sub(search,replace, path)

            if hash not in index:
                index[hash] = []
            index[hash].append((path, mtime, size))

def load_translate():
    global args
    global translate

    if not args.translate:
        return

    for search, replace in args.translate:
        expr = re.compile(search)
        translate.append((expr, replace))


def make_link(h):

    for path_, mtime, size in index[h]:
        if path_[0] == '/':
            path_ = path_[1:]
        dst = Path(args.root) / path_
        if os.path.lexists(dst):
            return
        src = Path(args.source) / h[0:2] / h[2:4] / h
        dst_dir = dst.parent
        if not os.path.isdir(dst_dir):
            if args.v > 0:
                print("D: create dir {}".format(dst_dir), file=sys.stderr)
            os.makedirs(dst_dir)
        if args.v > 0:
            print("D: create symlink {} -> {}".format(dst, src), file=sys.stderr)
        os.symlink(src, dst)


def main():

    global args
    global index

    parser = argparse.ArgumentParser()
    parser.add_argument('--source', '-s', required=True,
            help='Source of the archive. This is where all symlink will point to.')
    parser.add_argument('--root', '-r', required=True,
            help='This is the root of the created tree. It will not delete'
            ' or overwrite existing content.')
    parser.add_argument('--filter', '-f', action='append',
            help='If provided, only paths maching any of the filters will be'
            ' created. Shell path-expansion format.')
    parser.add_argument('index', nargs='*', 
            help='index files')
    parser.add_argument('-v', action='count', default=0,
            help='verbose')
    parser.add_argument('--translate', '-t', nargs=2, action='append',
            help='Translate prefixes. format is <pattern> <replace>, where'
            ' pattern and replace are regex and replace string as defined in re.sub')

    args = parser.parse_args()
    load_translate()

    for idx_file in args.index:
        load_index(idx_file)

    for h in index:
        make_link(h)


if __name__ == '__main__':
    main()




