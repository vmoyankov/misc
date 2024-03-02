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

import pathlib
import shutil
import subprocess  # noqa: S404
import sys
import typing

from . import util


if typing.TYPE_CHECKING:
    from typing import Final


FALSE_PROG: Final = pathlib.Path("/bin/false")
"""The program to replace the mock `ss` tool so it will fail."""


def replace_ss_with_bin_false(ctx: util.Context) -> None:
    """Replace the mock `ss` tool with a program that will fail."""
    ss_bin: Final = ctx.tempd / "bin/ss"
    print(f"Replacing {ss_bin} with {FALSE_PROG}")
    shutil.copy2(FALSE_PROG, ss_bin)

    # Make sure the replaced tool is still executable
    assert subprocess.check_output(
        ["sh", "-c", "command -v ss"],  # noqa: S603,S607
        encoding="UTF-8",
        env=ctx.env,
    ).splitlines() == [str(ss_bin)]

    # Make sure the replaced tool will indeed exit with an error
    ss_res: Final = subprocess.run(
        ["ss", "-tni"],  # noqa: S603,S607
        capture_output=True,
        check=False,
        encoding="UTF-8",
        env=ctx.env,
        stdin=subprocess.DEVNULL,
    )
    assert ss_res.returncode == 1  # this is /bin/false, right?
    assert not ss_res.stdout
    assert not ss_res.stderr


def test_no_output_without_ss() -> None:
    """If there is no `ss` tool at all, `tcp_stat` should exit at once."""
    print()
    with util.setup_ss_bin() as ctx:
        replace_ss_with_bin_false(ctx)

        print("Now let's see if tcp_stat will exit immediately with no output")
        res: Final = subprocess.run(
            [sys.executable, "-B", "-u", util.tcp_stat_path()],  # noqa: S603
            capture_output=True,
            check=False,
            encoding="UTF-8",
            env=ctx.env,
            stdin=subprocess.DEVNULL,
        )
        assert res.returncode
        assert not res.stdout
        assert res.stderr


def test_stop_when_ss_disappears() -> None:
    """Let `tcp_stat` output a single line, then make `ss` go away."""
    print()
    session: Final = util.TSTAT_OUTPUT_SINGLE_1
    with util.setup_ss_bin() as ctx:
        shutil.copy2(util.TEST_DATA_DIR / "ss-output-single-1.txt", ctx.ss_output)

        with util.run_tcp_stat(check_exit_code=False, env=ctx.env) as proc:
            assert proc.stdout is not None

            # First time around: no counters
            util.assert_initial(proc.stdout, session)

            # Second time around: no delta, but make `ss` disappear...
            util.assert_no_change(
                proc.stdout,
                session,
                update=lambda: replace_ss_with_bin_false(ctx),
            )

            # ...and now make sure it breaks
            line: Final = proc.stdout.readline()
            assert line == ""  # noqa: PLC1901  # we wouldn't like None, would we?

        res: Final = proc.wait()
        assert res > 0
