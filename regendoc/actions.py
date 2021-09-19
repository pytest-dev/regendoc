from __future__ import annotations
import os
import subprocess
import shutil
from pathlib import Path

from dataclasses import dataclass
from typing import Callable
from logging import getLogger

log = getLogger(__name__)


def write(target_dir: Path, action: Action) -> None:
    # XXX: insecure
    assert not action.target.startswith(os.path.sep), action.target
    log.debug("write to [bold]%s[/]", action.target)
    target = target_dir.joinpath(action.target)
    target.parent.mkdir(exist_ok=True, parents=True)
    target.write_text(action.content)


def process(target_dir: Path, action: Action) -> str:
    if action.cwd:

        # the cwd option is insecure and used for examples
        # that already have all files in place
        # like an examples folder for example
        if action.cwd is not None and action.cwd == Path("."):
            assert action.file is not None
            src = action.file.parent
            target_dir = target_dir / "CWD"
        else:
            src = action.file.parent.joinpath(action.cwd)

            target_dir = target_dir.joinpath(action.cwd)
        shutil.copytree(src, target_dir)

    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)
    target = action.target
    log.debug("popen %r\n  cwd=%s", target, target_dir)
    output = subprocess.run(
        target,
        shell=True,
        cwd=target_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0,
        encoding="utf-8",
    )

    return output.stdout


def wipe(target_dir: Path, action: Action) -> None:
    log.debug("wiping targetdir [bold warning]%s[/]", target_dir)
    shutil.rmtree(target_dir)
    os.mkdir(target_dir)


ACTIONS = {"shell": process, "wipe": wipe, "write": write}

COMMAND_TYPE = Callable[[Path, "Action"], "str|None"]


@dataclass
class Action:
    command: COMMAND_TYPE
    target: str
    content: str
    file: Path
    new_content: str | None = None
    cwd: Path | None = None
    indent: int = 0
    line: int = 0

    def __call__(self, target_dir: Path) -> str | None:
        return self.command(target_dir, self)
