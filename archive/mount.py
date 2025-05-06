#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import csv
import errno
import logging
import os
import pathlib
import stat
import sys

from argparse import ArgumentParser, FileType
from dataclasses import dataclass, field

import pyfuse3
import trio


from pyfuse3 import FUSEError

try:
    import faulthandler
except ImportError:
    pass
else:
    faulthandler.enable()

log = logging.getLogger(__name__)


@dataclass
class FileEntry:
    is_dir: bool = False
    inode: int = 0
    filename: str = ""
    path: str = ""
    mtime: int = 0
    hash_: str = ""
    size: int = 0
    files: list[FileEntry] = field(default_factory=list)
    dir_path: str = ""
    parent: FileEntry | None = None


class ArchiveFs(pyfuse3.Operations):
    enable_writeback_cache = True

    def __init__(self, index_file, base_path):
        log.debug("__init__")
        super().__init__()
        self.index_file = index_file
        self.base_path = base_path
        self.last_inode = 0
        self.entries_by_inode = {}
        self.openfd = set()
        self.paths = {}
        self._load_index()

    def _load_index(self):
        with self.index_file as f:
            reader = csv.reader(f)

            root = FileEntry()
            root.is_dir = True
            self.last_inode += 1
            self.entries_by_inode[self.last_inode] = root
            root.is_dir = True
            root.path = "/"
            self.paths["/"] = root

            for row in reader:
                hash_, mtime, size, path = row[:]
                entry = FileEntry()
                pp = pathlib.PurePath(path)
                self.last_inode += 1
                self.entries_by_inode[self.last_inode] = entry
                entry.inode = self.last_inode
                entry.path = path
                entry.filename = pp.name
                entry.dir_path = pp.parent.as_posix()
                entry.parent = self._get_dir(entry.dir_path)
                entry.hash_ = hash_

                entry.mtime = int(mtime)
                entry.size = int(size)

                entry.parent.files.append(entry)
                self.paths[path] = entry

    def _get_dir(self, path: str) -> FileEntry:
        log.debug("_get_dir %s", path)
        try:
            entry = self.paths[path]
            assert entry.is_dir
        except KeyError:
            entry = FileEntry()
            pp = pathlib.PurePath(path)
            self.last_inode += 1
            self.entries_by_inode[self.last_inode] = entry
            entry.inode = self.last_inode
            entry.path = path
            entry.filename = pp.name
            entry.dir_path = pp.parent.as_posix()
            entry.parent = self._get_dir(entry.dir_path)

            entry.mtime = 0
            entry.size = 0
            entry.is_dir = True

            entry.parent.files.append(entry)
            self.paths[path] = entry
        return entry

    async def getattr(self, inode, ctx=None):
        log.debug("getattr %d", inode)
        attr = pyfuse3.EntryAttributes()
        try:
            entry = self.entries_by_inode[inode]
        except KeyError:
            return attr
        if entry.is_dir:
            attr.st_mode = pyfuse3.ModeT(stat.S_IFDIR | 0o755)
            attr.st_size = 0
            stamp = 0
        else:
            attr.st_mode = pyfuse3.ModeT(stat.S_IFREG | 0o444)
            attr.st_size = entry.size
            stamp = int(entry.mtime * 1e9)

        attr.st_atime_ns = stamp
        attr.st_ctime_ns = stamp
        attr.st_mtime_ns = stamp
        attr.st_gid = os.getgid()
        attr.st_uid = os.getuid()
        attr.st_ino = inode
        return attr

    async def lookup(self, parent_inode, name, ctx=None):
        name = os.fsdecode(name)
        log.debug("lookup for %s in %d", name, parent_inode)

        dir_entry = self.entries_by_inode[parent_inode]
        for file_entry in dir_entry.files:
            if file_entry.filename == name:
                inode = file_entry.inode
                attr = await self.getattr(inode)
                return attr

        # Not found, return st_ino = 0
        attr = pyfuse3.EntryAttributes()
        attr.st_ino = pyfuse3.InodeT(0)
        return attr

    async def opendir(self, inode, ctx):
        log.debug("opendir %s", inode)
        try:
            entry = self.entries_by_inode[inode]
            if not entry.is_dir:
                raise pyfuse3.FUSEError(errno.ENOENT)
        except KeyError:
            raise pyfuse3.FUSEError(errno.ENOENT)

        return inode

    async def readdir(self, fh, start_id, token):
        log.debug("readdir %s %d", fh, start_id)
        assert fh in self.entries_by_inode
        dir = self.entries_by_inode[fh]
        for fid in range(start_id, len(dir.files)):
            f_entry = dir.files[fid]
            log.debug(
                "readdir_reply %s inode=%d next=%d",
                f_entry.filename,
                f_entry.inode,
                fid + 1,
            )
            if not pyfuse3.readdir_reply(
                token,
                f_entry.filename.encode("utf8"),
                await self.getattr(f_entry.inode),
                fid + 1,
            ):
                break

    async def open(self, inode, flags, ctx):
        log.debug("open %d %d", inode, flags)
        if inode not in self.entries_by_inode:
            raise pyfuse3.FUSEError(errno.ENOENT)
        if flags & os.O_RDWR or flags & os.O_WRONLY:
            raise pyfuse3.FUSEError(errno.EACCES)
        entry = self.entries_by_inode[inode]
        if entry.is_dir:
            raise pyfuse3.FUSEError(errno.EACCES)
        hash_ = entry.hash_
        filename = os.path.join(self.base_path, hash_[0:2], hash_[2:4], hash_)
        log.debug("Openinig %s", filename)
        try:
            fh = os.open(filename, flags)
        except OSError as exc:
            raise FUSEError(exc.errno)
        self.openfd.add(fh)
        return pyfuse3.FileInfo(fh=fh)

    async def read(self, fh, off, size):
        log.debug("read fh=%d off=%d size=%d", fh, off, size)
        assert fh in self.openfd
        os.lseek(fh, off, os.SEEK_SET)
        return os.read(fh, size)

    async def release(self, fh):
        log.debug("release fh=%d", fh)
        assert fh in self.openfd
        try:
            os.close(fh)
        except OSError as exc:
            raise FUSEError(exc.errno)


def init_logging(debug=False):
    formatter = logging.Formatter(
        "%(asctime)s.%(msecs)03d %(threadName)s: [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    if debug:
        handler.setLevel(logging.DEBUG)
        root_logger.setLevel(logging.DEBUG)
    else:
        handler.setLevel(logging.INFO)
        root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)


def parse_args(args):
    """Parse command line"""

    parser = ArgumentParser()

    parser.add_argument(
        "index_file",
        type=FileType("r", encoding="utf-8"),
        help="Path to the index file",
    )
    parser.add_argument(
        "base_path",
        type=pathlib.Path,
        help="Base path of the files",
    )
    parser.add_argument("mountpoint", type=str, help="Where to mount the file system")
    parser.add_argument(
        "--debug", action="store_true", default=False, help="Enable debugging output"
    )
    parser.add_argument(
        "--debug-fuse",
        action="store_true",
        default=False,
        help="Enable FUSE debugging output",
    )
    return parser.parse_args(args)


def main():
    options = parse_args(sys.argv[1:])
    init_logging(options.debug)
    archive_fs = ArchiveFs(options.index_file, options.base_path)

    log.debug("Mounting...")
    fuse_options = set(pyfuse3.default_options)
    fuse_options.add("fsname=passthroughfs")
    if options.debug_fuse:
        fuse_options.add("debug")
    pyfuse3.init(archive_fs, options.mountpoint, fuse_options)

    try:
        log.debug("Entering main loop..")
        trio.run(pyfuse3.main)
    except:
        pyfuse3.close(unmount=False)
        raise

    log.debug("Unmounting..")
    pyfuse3.close()


if __name__ == "__main__":
    main()
