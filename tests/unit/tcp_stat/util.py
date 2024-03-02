# Copyright 2024 Peter Pentchev <roam@ringlet.net>
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
"""A couple of basic functionality tests for the tcpstat utility."""

from __future__ import annotations

import contextlib
import dataclasses
import pathlib
import signal
import subprocess  # noqa: S404
import sys
import tempfile
import time
import typing

import utf8_locale


if typing.TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    from typing import IO, Final


TOP_DIR: Final = pathlib.Path(__file__).absolute().parent.parent.parent.parent
"""The path to the top-level directory of the 'misc' repository."""

TEST_DATA_DIR: Final = TOP_DIR / "tests/data/tcp_stat"
"""The path to the directory containing the `tcp_stat` test output files."""

SS_TEXT: Final = """#!/bin/sh

set -e

unset opt_info opt_numeric opt_tcp
while getopts 'int' o; do
	case "$o" in
		i)
			opt_info=1
			;;

		n)
			opt_numeric=1
			;;

		t)
			opt_tcp=1
			;;

		*)
			echo 'Unexpected command-line option passed to ss' 1>&2
			exit 1
			;;
	esac
done

if [ -z "$opt_info" ] || [ -z "$opt_numeric" ] || [ -z "$opt_tcp" ]; then
	echo 'Expected all of the -i, -n, and -t options to be passed to ss' 1>&2
	exit 1
fi

cat -- '{ss_output}'
"""
"""Our mock-up socket status tool."""


TSTAT_OUTPUT_SINGLE_1: Final = "192.168.1.184:59738-185.117.82.66:22"
"""The first line of output in the "single TCP session" test."""


@dataclasses.dataclass(frozen=True)
class Context:
    """Runtime context for the `tcp_stat` unit tests."""

    env: dict[str, str]
    """The environment variables to pass to the subprocess."""

    tempd: pathlib.Path
    """The base temporary directory to use."""

    ss_output: pathlib.Path
    """The path to the output file that the mock sockstat will produce next."""


@contextlib.contextmanager
def setup_tempdir(*, prefix: str | None = None) -> Iterator[pathlib.Path]:
    """Create a temporary directory, provide it as a `pathlib.Path` object."""
    with tempfile.TemporaryDirectory(prefix=prefix) as tempd_obj:
        tempd: Final = pathlib.Path(tempd_obj)
        print(f"Using {tempd} as a temporary directory")

        yield tempd


@contextlib.contextmanager
def setup_ss_bin() -> Iterator[Context]:
    """Set up the bin/ directory, return a usable environment."""
    with setup_tempdir(prefix="tcp-stat-test.") as tempd:
        bindir: Final = tempd / "bin"
        bindir.mkdir(mode=0o755)

        tmpdir: Final = tempd / "tmp"
        tmpdir.mkdir(mode=0o755)
        ss_output: Final = tmpdir / "ss-output-next.txt"

        ss_prog: Final = bindir / "ss"
        ss_prog.write_text(SS_TEXT.format(ss_output=ss_output), encoding="UTF-8")
        ss_prog.chmod(0o755)

        # Make sure we can find the mock tool we just created
        env: Final = utf8_locale.get_utf8_env()
        env["PATH"] = f"{bindir}:{env['PATH']}"

        # Make sure the tools output any lines one by one, immediately
        env["PYTHONUNBUFFERED"] = "1"

        # Make sure this works
        lines: Final = subprocess.check_output(
            ["sh", "-c", "command -v ss"],  # noqa: S603,S607
            encoding="UTF-8",
            env=env,
        ).splitlines()
        if lines != [str(ss_prog)]:
            raise RuntimeError(repr((tempd, lines)))

        yield Context(env=env, ss_output=ss_output, tempd=tempd)


def tcp_stat_path() -> pathlib.Path:
    """Get the path to the `tcp_stat` utility we are supposed to test."""
    return TOP_DIR / "tcp_stat.py"


@contextlib.contextmanager
def run_tcp_stat(
    *,
    env: dict[str, str],
    check_exit_code: bool = False,
) -> Iterator[subprocess.Popen[str]]:
    """Wrap the `tcp_stat` invocation in our start/terminate/kill/check harness."""
    with subprocess.Popen(
        [sys.executable, "-B", "-u", tcp_stat_path()],  # noqa: S603
        bufsize=0,
        encoding="UTF-8",
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
    ) as proc:
        assert proc.stdout is not None, repr(proc)
        try:
            yield proc

            print("Looks like we are done here")
            proc.terminate()
        finally:
            # Make sure we give the process time to output an exception backtrace
            time.sleep(0.5)

            # ...but don't take too long
            proc.kill()

        res: Final = proc.wait()
        if check_exit_code:
            # Make sure we told the program to stop
            assert res == -signal.SIGTERM, repr(res)


def assert_initial(stream: IO[str], session: str) -> None:
    """Make sure we get the initial line with the session prefix."""
    print("Waiting for the initial set of stats")
    assert stream.readline() == f"{session}\t\n"

    assert stream.readline() == "\n"


def assert_no_change(
    stream: IO[str],
    session: str,
    *,
    update: Callable[[], None] | None = None,
) -> None:
    """Make sure we get another set of data with no changes in the counters."""
    print("Waiting for another set of stats, no change")
    line = stream.readline()
    empty, prefix, contents = line.partition(session)
    assert not empty
    assert prefix == session
    assert contents.startswith("\t")
    assert "bytes_sent: 0\t" in contents
    assert "bytes_received: 0\t" in contents

    # Perform the update before we get the newline, it may be too late
    if update is not None:
        update()

    assert stream.readline() == "\n"


def assert_small_change(
    stream: IO[str],
    session: str,
    *,
    update: Callable[[], None] | None = None,
) -> None:
    """Make sure we get another set of data with only a small change in the counters."""
    print("Waiting for another set of stats, a small change")
    line = stream.readline()
    empty, prefix, contents = line.partition(session)
    assert not empty
    assert prefix == session
    assert contents.startswith("\t")
    assert "bytes_sent: 1\t" in contents
    assert "bytes_received: 10\t" in contents

    # Perform the update before we get the newline, it may be too late
    if update is not None:
        update()

    assert stream.readline() == "\n"
