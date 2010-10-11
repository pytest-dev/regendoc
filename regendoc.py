#!/usr/bin/python

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--update',
                    default=False,
                    action='store_true',
                    help='refresh the files instead of just reporting the difference')
parser.add_argument('files',
                    nargs='+',
                   help='the files to check/update')


def main():
    options = parser.parse_args()
    import py
    from simpledoctest.executer import Executor

    for name in options.files:
        tmpdir = py.path.local.make_numbered_dir(prefix='doc-exec-')
        p = py.path.local(name)
        print 'checking', name
        executor = Executor(
            file = p,
            tmpdir = tmpdir,
        )
        executor.run()


if __name__=='__main__':
    main()
