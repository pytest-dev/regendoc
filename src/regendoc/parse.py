from __future__ import annotations
from typing import NamedTuple, cast
from pathlib import Path
from .actions import COMMAND_TYPE, Action, write, process, wipe
from typing import Iterable


class LineBlock(NamedTuple):
    last_indent: int
    firstline: int
    items: list[str]


def dedent(line: str, last_indent: int) -> tuple[int, str]:
    if line[:last_indent].isspace():
        return last_indent, line[last_indent:]
    stripped = line.lstrip(" ")
    return len(line) - len(stripped), stripped


def blocks(lines: list[str]) -> list[LineBlock]:
    if not lines:
        return []
    result: list[LineBlock] = []
    firstline = 0
    last_indent = dedent(lines[0], 0)[0]
    items: list[str] = []
    for lineno, line in enumerate(lines):

        indent, rest = dedent(line, last_indent)

        if lineno and indent != last_indent:
            if items[0] == "\n":
                del items[0]
                firstline += 1
            if items and items[-1] == "\n":
                del items[-1]
            result.append(LineBlock(last_indent, firstline, items))
            items = [rest]
            last_indent = indent
            firstline = lineno

        else:
            last_indent = indent
            items.append(rest or "\n")

    else:
        result.append(LineBlock(indent, firstline, items))
    return result


def correct_content(content: Iterable[str], updates: list[Action]) -> list[str]:

    lines = list(content)
    for update in reversed(updates):
        line = update.line
        old_lines = len(update.content.splitlines())
        indent = " " * update.indent
        new_lines = [
            (indent + _line).rstrip() + "\n"
            for _line in cast(str, update.new_content).splitlines(True)
        ]
        lines[line + 1 : line + old_lines + 1] = new_lines

    return lines


def classify(
    lines: list[str], file: Path, indent: int = 0, line: int = 0
) -> Action | None:
    if not lines:
        return None
    first = lines[0]
    content = "".join(lines[1:])

    def at(command: COMMAND_TYPE, target: str, cwd: Path | None = None) -> Action:
        return Action(
            command=command,
            cwd=cwd,
            target=target,
            content=content,
            indent=indent,
            line=line,
            file=file,
        )

    if first.startswith("# content of"):
        target = first.strip().split()[-1]
        return at(write, target)
    elif first[0] == "$":
        cmd = first[1:].strip()
        return at(process, cmd)
    elif " $ " in first:
        cwd, target = first.split(" $ ")
        target = target.strip()
        return at(process, target, Path(cwd))
    elif not indent and any(".. regendoc:wipe" in x for x in lines):
        return at(wipe, "")

    return None


def parse_actions(content: list[str] | str, file: Path) -> Iterable[Action]:
    lines = content if isinstance(content, list) else content.splitlines(True)
    for indent, line, data in blocks(lines):
        action = classify(lines=data, indent=indent, line=line, file=file)
        if action is not None:
            yield action
