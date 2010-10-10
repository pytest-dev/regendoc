from simpledoctest.classify import classify

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
        'lineno': None,
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
        'lineno': None,
    }
    assert cmd == expected
