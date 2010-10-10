from simpledoctest.blockread import blocks
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
        (0, 1, ['some text\n', 'more text\n']),
        (0, 4, ['next block::\n']),
        (4, 6, ['indent\n', 'block\n']),
        (4, 9, ['with more\n']),
        (0, 11, ['.. directive:: test\n']),
        (4, 12, [':param: test\n']),
        (4, 14, ['text\n']),
    ]
    pprint.pprint(result)
    assert result == expected


