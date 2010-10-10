import py
from operator import itemgetter
a_c_t = itemgetter('action', 'target')


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
