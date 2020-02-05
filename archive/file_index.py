#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import csv
import glob
import os
import subprocess
import sys
import time


def index_file(csv_file, de):
    try:
        out = subprocess.check_output(['sha1sum', '-b', de.path])
    except subprocess.CalledProcessError as e:
        return
    hash, _ = out.split(maxsplit=1)
    stat = de.stat()
    csv_file.writerow((hash.decode('ascii'), int(stat.st_mtime), stat.st_size, de.path))


def index_dir(args, csv_file, path, last_indexed):

    if args.v:
        print('D {}'.format(path))
    sub_dirs = []
    files = []
    try:
        with os.scandir(path) as dir:
            for de in dir:
                if de.is_dir():
                    sub_dirs.append(de.path)
                    continue
                if not de.is_file():
                    continue
                if last_indexed is None:
                    files.append(de)
                else:
                    mtime = de.stat().st_mtime
                    if mtime > last_indexed:
                        files.append(de)
    except PermissionError as e:
        print(e, file=sys.stderr)
        return
    for de in files:
        if args.v:
            print('F {}'.format(de.path))
        index_file(csv_file, de)
    for path in sub_dirs:
        index_dir(args, csv_file, path, last_indexed)


def get_latest_index(args):
    index_files = glob.glob(args.index + '_' + '[0-9]'*8 + '-' + '[0-9]'*6)
    if len(index_files) == 0:
        return None
    for filename in sorted(index_files, reverse=True):
        try:
            with open(filename) as f:
                line = f.readline()
                last_time = int(line)
                if last_time > 0:
                    return last_time
        except Exception as e:
            print(e, file=sys.stderr)
            continue
    return None


def main():

    parser = argparse.ArgumentParser(description='Create index of files')
    parser.add_argument('dirs', nargs='+')
    parser.add_argument('-i', '--index', default='file_index',
            help='index file to be created. A suffix with the current time '
            'is added. Default to file_index')
    parser.add_argument('-n', '--newer', action='store_true',
            help='index only files changed since last index')
    parser.add_argument('-v', action='count', default=0,
            help='verbose')

    args = parser.parse_args()
    now = int(time.time()) - 1
    localtime = time.localtime(now)
    index_filename = "{}_{}".format(args.index, 
            time.strftime('%Y%m%d-%H%M%S', localtime))

    if args.newer:
        latest_index = get_latest_index(args)
    else:
        latest_index = None
    if latest_index is not None:
        print("Last indexed at " + time.strftime("%Y%m%d-%H:%M:%S", time.localtime(latest_index)))
    with open(index_filename, 'w') as index_file:
        print(now, file=index_file)
        csv_file = csv.writer(index_file)
        for path in args.dirs:
            index_dir(args, csv_file, path, latest_index)


if __name__ == '__main__':
    main()
