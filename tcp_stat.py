#!/usr/bin/env python3
# Copyright 2024 Venko Moyankov
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
"""Display the deltas in the output of the `ss` sockstat tool second by second."""

import argparse
import subprocess
import time


def main():
    """Parse command-line arguments, run `ss` repeatedly, process its output."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filter", help="Filter sessions by address:port")
    parser.add_argument("-F", "--params", help="Filter by param, coma separated list")
    parser.add_argument("-v", "--vertical", action="store_true")
    args = parser.parse_args()

    if args.vertical:
        delimiter = "\n"
    else:
        delimiter = "\t"

    if args.params:
        params = args.params.split(",")
    else:
        params = None

    sessions = {}
    while True:
        session = None
        res = subprocess.run(["ss", "-tni"], stdout=subprocess.PIPE, encoding="utf-8").stdout
        ignore_data = True
        for line in res.splitlines():
            fields = line.split()
            if fields and line[0][0].isalpha():
                if fields[0] == "ESTAB":
                    sid = "-".join(fields[3:5])
                    if sid not in sessions:
                        sessions[sid] = {}
                    session = sessions[sid]
                    ignore_data = False
                else:
                    ignore_data = True
            elif not ignore_data and any(field.startswith("bytes_sent:") for field in fields):
                if args.filter and args.filter not in sid:
                    continue
                stats = {}
                for word in fields[1:]:
                    if ":" in word:
                        k, v = word.split(":", 1)
                        try:
                            stats[k] = int(v)
                        except ValueError:
                            pass
                print(sid, end=delimiter)
                for k, v in stats.items():
                    if k not in session:
                        continue
                    if params and k not in params:
                        continue
                    d = v - session[k]
                    print("{}: {:d}".format(k, d), end=delimiter)
                sessions[sid] = stats
                print()

        time.sleep(1)
        print()


if __name__ == "__main__":
    main()
