import pprint
from regendoc import blocks
from regendoc import classify

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


def test_blocks():
    result = blocks(input_data_for_blocks.splitlines(True))
    expected = [
        # indent level, start line, lines
        (0, 1, ['some text\n', 'more text\n', '\n', 'next block::\n']),
        (4, 6, ['indent\n', '  block\n', '\n', 'with more\n']),
        (0, 11, ['.. directive:: test\n']),
        (4, 12, [':param: test\n', '\n', 'text\n'])
    ]
    pprint.pprint(result)
    assert result == expected


def test_classify_write():

    write = classify([
        '# content of test_foo.py\n',
        'def test()\n',
        '    pass\n',
    ])

    expected = {
        'action': 'write',
        'target': 'test_foo.py',
        'content': 'def test()\n    pass\n',
        'indent': 4,
        'line': None,
    }
    assert  write == expected


def test_classify_shell():
    cmd = classify(lines=[
        '$ py.test -x\n',
        'crud\n',
    ])
    expected = {
        'action': 'shell',
        'target': 'py.test -x',
        'content': 'crud\n',
        'indent': 4,
        'line': None,
    }
    assert cmd == expected
