import re

from itertools import count
from collections import defaultdict
import sys
import os


class SubstituteRegex:
    def __init__(self, match, replace):
        self.match = re.compile(match)
        self.replace = replace

    @classmethod
    def parse(cls, s):
        parts = s.split(s[0])
        assert len(parts) == 4
        return cls(match=parts[1], replace=parts[2])

    def __call__(self, line):
        return self.match.sub(self.replace, line)

    def __repr__(self):
        return "<Substituter {self.match.pattern!r} to {self.replace!r}>".format(
            self=self
        )


class SubstituteAddress:
    def __init__(self):
        self.match = re.compile(r"at 0x([0-9a-f]+)>")
        self.counter = count(1)
        self.known_addresses = defaultdict(lambda: next(self.counter))

    def replace_address(self, pattern_match: re.Match):
        group = pattern_match.group(1)

        return f"at 0xdeadbeef{self.known_addresses[group]:04x}>"

    def __call__(self, line: str) -> str:
        return self.match.sub(self.replace_address, line)


def default_substituters(targetdir):
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
