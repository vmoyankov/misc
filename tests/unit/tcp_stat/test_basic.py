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

import shutil
import typing

import pytest

from . import util


if typing.TYPE_CHECKING:
    from collections.abc import Callable
    from typing import IO, Final


TSTAT_OUTPUT_SINGLE_1: Final = "192.168.1.184:59738-185.117.82.66:22"
"""The first line of output in the "single TCP session" test."""


def test_single_no_output() -> None:
    """Test that tcp_stat processes the output of a single `ss` invocation correctly."""
    print()
    with util.setup_ss_bin() as ctx:
        # Let the mock sockstat output nothing at first
        ctx.ss_output.write_text("", encoding="UTF-8")

        with util.run_tcp_stat(env=ctx.env) as proc:
            assert proc.stdout is not None
            print("Waiting for an empty line (it should appear in exactly one second)")
            line: Final = proc.stdout.readline()
            assert line == "\n"


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


@pytest.mark.parametrize("suffix", ["single", "close-first", "close-last"])
def test_single_session_no_delta(suffix: str) -> None:
    """A single `ss` session, no changes between the `ss` invocations."""
    print()
    session: Final = TSTAT_OUTPUT_SINGLE_1
    with util.setup_ss_bin() as ctx:
        # Prepare the "single established session" output for the mock `ss` tool
        shutil.copy2(util.TEST_DATA_DIR / f"ss-output-{suffix}-1.txt", ctx.ss_output)

        with util.run_tcp_stat(env=ctx.env) as proc:
            assert proc.stdout is not None

            # First time around: no counters
            assert_initial(proc.stdout, session)

            # Second, third, and fourth times around: no deltas
            for _ in range(3):
                assert_no_change(proc.stdout, session)


@pytest.mark.parametrize("suffix", ["single", "close-first", "close-last"])
def test_single_session_small_delta(suffix: str) -> None:
    """A single `ss` session, a small change in the counters."""
    print()
    session: Final = TSTAT_OUTPUT_SINGLE_1
    with util.setup_ss_bin() as ctx:
        # Prepare the "single established session" output for the mock `ss` tool
        shutil.copy2(util.TEST_DATA_DIR / f"ss-output-{suffix}-1.txt", ctx.ss_output)

        with util.run_tcp_stat(env=ctx.env) as proc:
            assert proc.stdout is not None

            # First time around: no counters
            assert_initial(proc.stdout, session)

            # No change at first, but switch the file before the timer expires
            assert_no_change(
                proc.stdout,
                session,
                update=lambda: shutil.copy2(
                    util.TEST_DATA_DIR / f"ss-output-{suffix}-2.txt",
                    ctx.ss_output,
                ),
            )

            assert_small_change(proc.stdout, session)

            # And then no change on the next invocation, right?
            assert_no_change(proc.stdout, session)
