#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import collections
import csv
import hashlib
import os
import shutil
import subprocess
import sys
import time

index = set()

def load_index(path):
    """
    Load an index file. This data is later used to check if the file
    has changed and needs to be hashed. Stores only the minimum information
    needed to do the check.

    index file format:
    sha1,mtime,size,path
    """

    global index

    with open(path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            v = ':'.join((row[3],row[1],row[2]))
            index.add(hashlib.sha1(v.encode('utf-8')).digest())


def index_file(csv_file, de):
    try:
        out = subprocess.check_output(['sha1sum', '-b', de.path])
    except subprocess.CalledProcessError as e:
        return
    hash, _ = out.split(maxsplit=1)
    stat = de.stat()
    csv_file.writerow((hash.decode('ascii'), int(stat.st_mtime), stat.st_size, de.path))



def index_dir(args, csv_file, path):

    global index

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
                # add file for hasing only if this verion of the file is
                # not in the index
                f_stat = de.stat()
                mtime = int(f_stat.st_mtime)
                size = int(f_stat.st_size)
                v = '{}:{:d}:{:d}'.format(de.path, mtime, size)
                hv = hashlib.sha1(v.encode('utf-8')).digest()
                if hv in index:
                    if args.v:
                        print('- {} {} {}'.format(de.path, mtime, size))
                else:
                    if args.v:
                        print('+ {} {} {}'.format(de.path, mtime, size))
                    files.append(de)
    except PermissionError as e:
        print(e, file=sys.stderr)
        return
    for de in files:
        if args.v:
            print('F {}'.format(de.path))
        index_file(csv_file, de)
    for path in sub_dirs:
        index_dir(args, csv_file, path)


def main():

    parser = argparse.ArgumentParser(description='Create index of files')
    parser.add_argument('dirs', nargs='+')
    parser.add_argument('-i', '--index', default='file_index',
            help='Index file to be created or updated. A backup file is '
            'created. Default to file_index')
    parser.add_argument('-v', action='count', default=0,
            help='verbose')

    args = parser.parse_args()

    now = int(time.time()) - 1
    localtime = time.localtime(now)
    index_filename = "{}.tmp-{}".format(args.index, 
            time.strftime('%Y%m%d-%H%M%S', localtime))
    backup_filename = "{}.bak-{}".format(args.index,
            time.strftime('%Y%m%d-%H%M%S', localtime))

    if os.path.isfile(args.index):
        shutil.copyfile(args.index, index_filename)
        load_index(index_filename)


    with open(index_filename, 'a') as index_file:
        csv_file = csv.writer(index_file)
        for path in args.dirs:
            index_dir(args, csv_file, path)

    try:
        os.rename(args.index, backup_filename)
    except FileNotFoundError:
        pass
    os.rename(index_filename, args.index)

    if args.v:
        print("""
Flags:
-  File is found in the index and skipped
+  File is not found in the index and scheduled for hashing
D  Directory is scaned.
F  File is hashed
""")



if __name__ == '__main__':
    main()
