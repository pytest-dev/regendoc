import py
from operator import itemgetter
a_c_t = itemgetter('action', 'target')

from simpledoctest.blockread import correct_content
from simpledoctest.executer import Executor

example = py.path.local(__file__).dirpath().dirpath().join('example.txt')

def test_execute_actions(tmpdir):


    executer = Executor(
        file=example,
        tmpdir=tmpdir,
    )


    actions = list(executer.read_actions())

    interesting =  [a_c_t(x) for x in actions]
    expected = [
        ('write', 'test_simplefactory.py'),
        ('shell', 'py.test test_simplefactory.py')]

    assert interesting == expected


def test_execute_run(tmpdir):

    executor = Executor(
        file=example,
        tmpdir=tmpdir,
    )


    executor.run()

    assert tmpdir.join('test_simplefactory.py').check()


simple = """
an echo:
    $ echo hi
    oh no
"""

simple_corrected = simple.replace('oh no', 'hi')


def test_simple_new_content(tmpdir):
    fp = tmpdir.join('example.txt')
    fp.write(simple)
    runner = Executor(
        file = fp,
        tmpdir = tmpdir,
    )

    needed_update, = runner.run() # exactly one
    expeccted_update = {
        'action': 'shell',
        'target': 'echo hi',
        'content': 'oh no\n',
        'new_content': 'hi\n',
        'indent': 4,
        'line': 2,
    }
    assert needed_update == expeccted_update


def test_single_update():

    update = {
        'action': 'shell',
        'target': 'echo hi',
        'content': 'oh no\n',
        'new_content': 'hi\n',
        'indent': 4,
        'line': 2,
    }

    corrected = correct_content(simple, [update])
    assert corrected == simple_corrected
