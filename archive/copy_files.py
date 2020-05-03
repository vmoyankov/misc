#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import csv
import argparse
import time

index = {}

def load_index(index_filename):

    global index

    with open(index_filename) as index_file:
        reader = csv.reader(index_file)
        for row in reader:
            hash, mtime, size, path = row[:]
            if hash not in index:
                index[hash] = []
            index[hash].append((path, mtime, size))


def mkdir(out, hash):
    dst = os.path.join(out,hash[0:2],hash[2:4])
    if os.path.isdir(dst):
        return
    if args.v:
        print("D: Makedir {}".format(dst))
    os.makedirs(dst)

def copy_file(hash_, out):

    # Get list of files with the same hash ordered by -mtime
    for (path, mtime, size) in sorted(index[hash_], key=lambda x:x[1], reverse=True):
        try:
            stat = os.stat(path)
        except FileNotFoundError:
            continue
        if int(stat.st_mtime) == int(mtime) and stat.st_size == int(size):
            dst = os.path.join(out, hash_[0:2], hash_[2:4], hash_)
            mkdir(out, hash_)
            if os.path.isfile(dst):
                if args.v:
                    print("D: Exists {}".format(hash_))
                return
            if args.v:
                print("D: Copy {} from {}".format(hash_, path))
            shutil.copyfile(path, dst)
            return
    print("E: {} not found!".format(hash_))


def copy_index(out):
    global args

    dst_filename = 'file_index.bak-{}'.format(
            time.strftime('%Y%m%d-%H%M%S')
            )
    dst = os.path.join(out, dst_filename)
    shutil.copyfile(args.index, dst)



def main():
    global args
    global index

    parser = argparse.ArgumentParser(
            description='Copy indexed files to the archive')
    parser.add_argument('--out', help="Output directory")
    parser.add_argument('index', nargs='+',
            help='One or more index files to be processed. Each file listed '
            'in any of the indexes will be copied.')
    parser.add_argument('-s', '--source', help='Source name. Index file will be'
            ' copied with this name in the target dir. If not provided,'
            ' index file will not be copied. Typically this is the hostname.')
    parser.add_argument('-v', action='count', default=0,
            help='verbose')

    args = parser.parse_args()

    for idx_file in args.index:
        load_index(idx_file)
    for h in index:
        copy_file(h, args.out)

    #copy_index(args.out)


if __name__ == '__main__':
    main()
