from regendoc import blocks
import pprint

input_data = """
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
    result = blocks(input_data.splitlines(True))
    expected = [
        # indent level, start line, lines
        (0, 1, ['some text\n', 'more text\n', '\n', 'next block::\n']),
        (4, 6, ['indent\n', '  block\n', '\n', 'with more\n']),
        (0, 11, ['.. directive:: test\n']),
        (4, 12, [':param: test\n', '\n', 'text\n'])
    ]
    pprint.pprint(result)
    assert result == expected


