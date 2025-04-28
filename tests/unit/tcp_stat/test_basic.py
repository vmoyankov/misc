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
    from typing import Final


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


@pytest.mark.parametrize("suffix", ["single", "close-first", "close-last"])
def test_single_session_no_delta(suffix: str) -> None:
    """A single `ss` session, no changes between the `ss` invocations."""
    print()
    session: Final = util.TSTAT_OUTPUT_SINGLE_1
    with util.setup_ss_bin() as ctx:
        # Prepare the "single established session" output for the mock `ss` tool
        shutil.copy2(util.TEST_DATA_DIR / f"ss-output-{suffix}-1.txt", ctx.ss_output)

        with util.run_tcp_stat(env=ctx.env) as proc:
            assert proc.stdout is not None

            # First time around: no counters
            util.assert_initial(proc.stdout, session)

            # Second, third, and fourth times around: no deltas
            for _ in range(3):
                util.assert_no_change(proc.stdout, session)


@pytest.mark.parametrize("suffix", ["single", "close-first", "close-last"])
def test_single_session_small_delta(suffix: str) -> None:
    """A single `ss` session, a small change in the counters."""
    print()
    session: Final = util.TSTAT_OUTPUT_SINGLE_1
    with util.setup_ss_bin() as ctx:
        # Prepare the "single established session" output for the mock `ss` tool
        shutil.copy2(util.TEST_DATA_DIR / f"ss-output-{suffix}-1.txt", ctx.ss_output)

        with util.run_tcp_stat(env=ctx.env) as proc:
            assert proc.stdout is not None

            # First time around: no counters
            util.assert_initial(proc.stdout, session)

            # No change at first, but switch the file before the timer expires
            util.assert_no_change(
                proc.stdout,
                session,
                update=lambda: shutil.copy2(
                    util.TEST_DATA_DIR / f"ss-output-{suffix}-2.txt",
                    ctx.ss_output,
                ),
            )

            util.assert_small_change(proc.stdout, session)

            # And then no change on the next invocation, right?
            util.assert_no_change(proc.stdout, session)
