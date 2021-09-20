from __future__ import annotations

import re

from itertools import count
from collections import defaultdict
import sys
import os
from pathlib import Path


class SubstituteRegex:
    def __init__(self, match: str, replace: str) -> None:
        try:
            self.match = re.compile(match)
        except re.error as e:
            raise ValueError(match) from e
        self.replace = replace

    @classmethod
    def parse(cls: type[SubstituteRegex], s: str) -> SubstituteRegex:
        parts = s.split(s[0])
        assert len(parts) == 4
        return cls(match=parts[1], replace=parts[2])

    def __call__(self, line: str) -> str:
        return self.match.sub(self.replace, line)

    def __repr__(self) -> str:
        return "<Substituter {self.match.pattern!r} to {self.replace!r}>".format(
            self=self
        )


class SubstituteAddress:
    def __init__(self) -> None:
        self.match = re.compile(r"at 0x([0-9a-f]+)>")
        self.counter = count(1)
        self.known_addresses: dict[str, int] = defaultdict(lambda: next(self.counter))

    def replace_address(self, pattern_match: re.Match[str]) -> str:
        group = pattern_match.group(1)

        return f"at 0xdeadbeef{self.known_addresses[group]:04x}>"

    def __call__(self, line: str) -> str:
        return self.match.sub(self.replace_address, line)


def default_substituters(targetdir: Path) -> list[SubstituteAddress | SubstituteRegex]:
    return [
        SubstituteRegex(
            match=re.escape(os.fspath(targetdir)), replace="/path/to/example"
        ),
        SubstituteRegex(match=re.escape(os.getcwd()), replace="$PWD"),
        SubstituteAddress(),
        SubstituteRegex(
            match=re.escape(sys.prefix) + ".*?site-packages", replace="$PYTHON_SITE"
        ),
        SubstituteRegex(match=re.escape(sys.prefix), replace="$PYTHON_PREFIX"),
    ]
