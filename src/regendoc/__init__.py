from __future__ import annotations
import os
from regendoc.actions import Action
from typing import Callable, Iterator, Sequence
import contextlib
import tempfile
from pathlib import Path
from .parse import parse_actions, correct_content
from .substitute import SubstituteAddress, SubstituteRegex, default_substituters
import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.progress import BarColumn, Progress, TextColumn, TimeRemainingColumn

log = logging.getLogger("regendoc")
log.propagate = False

NORMALIZERS = Sequence[Callable[[str], str]]


def normalize_content(content: str, operators: NORMALIZERS) -> str:
    lines = content.splitlines(True)
    result = []
    for line in lines:
        for op in operators:
            line = op(line)
        result.append(line)
    return "".join(result)


def check_file(
    path: Path, content: list[str], tmp_dir: Path, normalize: NORMALIZERS
) -> list[Action]:
    needed_updates = []
    for action in parse_actions(content, file=path):

        new_content = action(tmp_dir)
        if new_content:
            action.new_content = normalize_content(new_content, normalize)
            needed_updates.append(action)
    return needed_updates


def print_diff(action: Action, console: Console) -> None:
    content, out = action.content, action.new_content
    assert out is not None

    if out != content:
        import difflib

        differ = difflib.Differ()
        outl = out.splitlines(True)
        contl = content.splitlines(True)
        lines = differ.compare(contl, outl)

        styles = {"+": "bold green", "-": "bold red", "?": "bold blue"}
        if lines:
            console.print("$", action.target, style="bold blue")
        for line in lines:
            style = styles.get(line[0])
            console.print(line, style=style, end="")


def mktemp(rootdir: Path | None, name: str) -> Path:
    if rootdir is not None:
        return Path(rootdir)
    root = tempfile.gettempdir()
    rootdir = Path(root, "regendoc-tmpdirs")
    rootdir.mkdir(exist_ok=True)
    return Path(tempfile.mkdtemp(prefix=name + "-", dir=rootdir))


@contextlib.contextmanager
def ux_setup(verbose: bool) -> Iterator[Progress]:

    columns = [
        TextColumn("[progress.description]{task.description}"),
        TextColumn("[progress.percentage]{task.completed:3.0f}/{task.total:3.0f}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
    ]
    with Progress(
        *columns,
    ) as progress:

        handler = RichHandler(
            markup=True,
            rich_tracebacks=True,
            show_path=False,
            log_time_format="[%H:%m]",
            console=progress.console,
        )
        log.addHandler(handler)
        log.setLevel(logging.DEBUG if verbose else logging.INFO)

        yield progress


def run(
    files: list[Path],
    update: bool,
    normalize: list[SubstituteRegex | SubstituteAddress] | None = None,
    rootdir: Path | None = None,
    def_name: str | None = None,
    verbose: bool = False,
    columns: int | None = None,
) -> None:
    parsed_normalize = normalize or []

    cwd = Path.cwd()
    tmpdir: Path = mktemp(rootdir, cwd.name)

    with ux_setup(verbose) as progress:
        if columns is not None:
            os.environ["COLUMNS"] = str(columns)
        task_id = progress.add_task(description="progressing files")
        for num, name in enumerate(progress.track(files, task_id=task_id)):

            targetdir = tmpdir.joinpath("%s-%d" % (os.path.basename(name), num))
            with open(name) as fp:
                content = list(fp)
            targetdir.mkdir()
            log.info(f"[bold]{name}[/bold]")
            updates = check_file(
                path=name,
                content=content,
                tmp_dir=targetdir,
                normalize=default_substituters(targetdir) + parsed_normalize,
            )
            for action in updates:
                print_diff(action, progress.console)
            if update:
                corrected = correct_content(content, updates)
                with open(name, "w") as f:
                    f.writelines(corrected)
