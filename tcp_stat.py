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

from __future__ import annotations

import argparse
import contextlib
import subprocess  # noqa: S404
import time


def main() -> None:  # noqa: C901,PLR0912  # Split it up... later
    """Parse command-line arguments, run `ss` repeatedly, process its output."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filter", help="Filter sessions by address:port")
    parser.add_argument("-F", "--params", help="Filter by param, comma-separated list")
    parser.add_argument("-v", "--vertical", action="store_true")
    args = parser.parse_args()

    delimiter = "\n" if args.vertical else "\t"

    params = args.params.split(",") if args.params else None

    sessions: dict[str, dict[str, int]] = {}
    while True:  # noqa: PLR1702  # Split it up... later
        session = None
        res = subprocess.check_output(["ss", "-tni"], encoding="utf-8")  # noqa: S603,S607
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
                if session is None:
                    raise RuntimeError(repr((sessions, ignore_data, line)))
                if args.filter and args.filter not in sid:
                    continue
                stats = {}
                for word in fields[1:]:
                    if ":" in word:
                        f_key, f_value = word.split(":", 1)
                        with contextlib.suppress(ValueError):
                            stats[f_key] = int(f_value)
                print(sid, end=delimiter)
                for s_key, s_value in stats.items():
                    if s_key not in session:
                        continue
                    if params and s_key not in params:
                        continue
                    delta = s_value - session[s_key]
                    print(f"{s_key}: {delta:d}", end=delimiter)
                sessions[sid] = stats
                print()

        time.sleep(1)
        print()


if __name__ == "__main__":
    main()
