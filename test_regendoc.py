from __future__ import annotations
import os
import pytest
from pathlib import Path
import subprocess
from regendoc.parse import (
    blocks,
    correct_content,
    classify,
    parse_actions,
    LineBlock as LB,
)
from regendoc.actions import Action, process, write

from regendoc import run, check_file


@pytest.fixture
def fake_file(tmp_path: Path) -> Path:
    return tmp_path / "mess.rst"


input_data_for_blocks = """
some text
more text

next block::

    indent
      block

    with more

.. directive:: test
    :param: test

    text
"""


simple = """
an echo:
    $ echo hi
    oh no
"""

input_data_for_blocks_md = """
some text
more text

```python
# content of test_foo.py

def test_fun(hi):
    pass
```

```text
$ pytest test_foo.py
hello
```
"""


simple_corrected = simple.replace("oh no", "hi")


indented = r"""
an extra echo:
    $ printf "hi\n\nextra hi\n"
    hi

    extra hi
"""


def test_blocks() -> None:
    result = blocks(input_data_for_blocks.splitlines(True), is_markdown=False)
    expected = [
        # indent level, start line, lines
        LB(0, 1, ["some text\n", "more text\n", "\n", "next block::\n"]),
        LB(4, 6, ["indent\n", "  block\n", "\n", "with more\n"]),
        LB(0, 11, [".. directive:: test\n"]),
        LB(4, 12, [":param: test\n", "\n", "text\n"]),
    ]
    assert result == expected


def test_blocks_markdown() -> None:
    result = blocks(input_data_for_blocks_md.splitlines(True), is_markdown=True)
    expected = [
        # indent level, start line, lines
        LB(0, 0, ["\n", "some text\n", "more text\n", "\n", "```python\n"]),
        LB(
            0,
            5,
            ["# content of test_foo.py\n", "\n", "def test_fun(hi):\n", "    pass\n"],
        ),
        LB(0, 10, ["```\n", "\n", "```text\n"]),
        LB(0, 12, ["$ pytest test_foo.py\n", "hello\n"]),
    ]
    import rich

    rich.print(result)
    assert result == expected


def test_classify_write(fake_file: Path) -> None:

    write_result = classify(
        ["# content of test_foo.py\n", "def test()\n", "    pass\n"], file=fake_file
    )

    expected = Action(
        command=write,
        cwd=None,
        target="test_foo.py",
        content="def test()\n    pass\n",
        indent=0,
        line=0,
        file=fake_file,
    )
    assert write_result == expected


def test_classify_shell(fake_file: Path) -> None:
    cmd = classify(lines=["$ py.test -x\n", "crud\n"], file=fake_file)
    expected = Action(
        command=process,
        cwd=None,
        target="py.test -x",
        content="crud\n",
        indent=0,
        line=0,
        file=fake_file,
    )
    assert cmd == expected


def test_classify_chdir_shell(fake_file: Path) -> None:
    cmd = classify(lines=["testing $ echo hi\n", "crud\n"], file=fake_file)

    expected = Action(
        command=process,
        cwd=Path("testing"),
        target="echo hi",
        content="crud\n",
        indent=0,
        line=0,
        file=fake_file,
    )

    assert cmd == expected


EXAMPLE_DOC = """\
a simple test function call with one argument factory
==============================================================
the function argument.  Let's look at a simple self-contained
example that you can put into a test module::
    # content of: test_simplefactory.py
    def pytest_funcarg__myfuncarg(request):
        return 42
    def test_function(myfuncarg):
        assert myfuncarg == 17
.. code-block:: bash
    $ py.test test_simplefactory.py
    output should be here - but thats nice for testing
the end.
"""


@pytest.fixture
def example(tmp_path: Path) -> Path:
    p = tmp_path.joinpath("example.txt")

    p.write_text(EXAMPLE_DOC)
    return p


def test_simple_new_content(tmp_path: Path) -> None:

    (needed_update,) = check_file(
        path=Path("example"),
        content=simple.splitlines(True),
        tmp_dir=tmp_path,
        normalize=[],
    )

    expected_update = Action(
        command=process,
        cwd=None,
        file=Path("example"),
        target="echo hi",
        content="oh no\n",
        new_content="hi\n",
        indent=4,
        line=2,
    )
    print(needed_update)
    assert needed_update == expected_update


def test_single_update(fake_file: Path) -> None:
    update = Action(
        command=process,
        target="echo hi",
        content="oh no\n",
        new_content="hi\n",
        indent=4,
        line=2,
        file=fake_file,
    )

    corrected = correct_content(simple.splitlines(True), [update])
    assert corrected == simple_corrected.splitlines(True)


def test_stripped_whitespace_no_update(tmp_path: Path) -> None:
    raw = indented.splitlines(True)
    (action,) = check_file(
        path=Path("example"), content=raw, tmp_dir=tmp_path, normalize=[]
    )
    assert action.content == action.new_content
    corrected = correct_content(raw, [action])
    assert raw == corrected


def test_actions_of(example: Path, fake_file: Path) -> None:

    actions = list(parse_actions(example.read_text().splitlines(), file=fake_file))

    interesting = [(action.command, action.target) for action in actions]
    expected = [
        (write, "test_simplefactory.py"),
        (process, "py.test test_simplefactory.py"),
    ]

    assert interesting == expected


def test_check_file(tmp_path: Path, example: Path) -> None:

    check_file(
        path=Path("test.txt"),
        content=example.read_text().splitlines(True),
        tmp_dir=tmp_path,
        normalize=[],
    )
    assert tmp_path.joinpath("test_simplefactory.py").is_file()


def test_main_no_update(tmp_path: Path, example: Path) -> None:
    run([example], update=False, rootdir=tmp_path)
    # check for the created tmpdir

    assert tmp_path.joinpath("example.txt-0").is_dir()


def test_empty_update(tmp_path: Path) -> None:
    simple_fp = tmp_path / "simple.txt"
    simple_fp.write_text("")
    run([simple_fp], update=True, rootdir=tmp_path)
    corrected = simple_fp.read_text()
    assert corrected == ""


def test_main_update(tmp_path: Path) -> None:
    simple_fp = tmp_path / "simple.txt"
    simple_fp.write_text(simple)
    run([simple_fp], update=True, rootdir=tmp_path)
    corrected = simple_fp.read_text()

    assert corrected == simple_corrected


def test_docfile_chdir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "nested/file"
    path.parent.mkdir()

    path.write_text("some text\n")
    monkeypatch.chdir(path.parent)
    filename = tmp_path / "test.txt"
    content = ["some shell test\n", "  nested $ cat file\n", "  some other text\n"]

    (action,) = parse_actions(content, file=filename)
    excpected_action = Action(
        command=process,
        content="some other text\n",
        cwd=Path("nested"),
        file=filename,
        indent=2,
        line=1,
        target="cat file",
    )
    assert action == excpected_action

    needed_updates = check_file(
        path=tmp_path / "example.txt",
        content=content,
        tmp_dir=tmp_path / "tmp",
        normalize=[],
    )

    assert needed_updates
    # is it copied?
    assert tmp_path.joinpath("tmp/nested/file").is_file()


def test_parsing_problem(tmp_path: Path) -> None:
    simple_fp = tmp_path.joinpath("index.txt")
    simple_fp.write_text(example_index)

    run([simple_fp], update=True, rootdir=tmp_path)
    corrected = simple_fp.read_text()
    assert corrected == example_index


example_index = """
py.test: no-boilerplate testing with Python
==============================================

.. toctree::
"""


def test_wipe(tmp_path: Path) -> None:
    fp = tmp_path / "example.txt"
    fp.write_text(".. regendoc:wipe\n")
    check_file(
        path=fp, content=fp.read_text().splitlines(), tmp_dir=tmp_path, normalize=[]
    )

    assert not list(tmp_path.iterdir())


def test_dotcwd(tmp_path: Path) -> None:
    name = tmp_path / "src/file"
    name.parent.mkdir()
    name.touch()
    tmp = tmp_path / "tmp"
    tmp.mkdir()
    check_file(
        path=name,
        content=["   . $ echo hi"],
        tmp_dir=tmp,
        normalize=[],
    )


def test_cli(tmp_path: Path) -> None:
    root = tmp_path.joinpath("tmp")
    root.mkdir()
    sample = tmp_path.joinpath("example.txt")
    sample.write_text(simple)
    subprocess.check_call(["regendoc", os.fspath(sample), "--rootdir", os.fspath(root)])
