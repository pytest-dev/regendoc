from simpledoctest.classify import classify

def test_classify_write():

    write = classify([
        '# content of test_foo.py\n',
        'def test()\n',
        '    pass\n',
    ])

    expected = 'write', 'test_foo.py', 'def test()\n    pass\n'
    assert  write == expected

def test_classify_shell():
    cmd = classify([
        '$ py.test -x\n',
        'crud\n',
    ])
    expected = 'exec', 'py.test -x', 'crud\n'
    assert cmd == expected
