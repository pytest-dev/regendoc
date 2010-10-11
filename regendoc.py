#!/usr/bin/python

import argparse
import subprocess

from simpledoctest.blockread import blocks

parser = argparse.ArgumentParser()
parser.add_argument('--update',
                    default=False,
                    action='store_true',
                    help='refresh the files instead of just reporting the difference')
parser.add_argument('files',
                    nargs='+',
                   help='the files to check/update')


def classify(lines, indent=4, line=None):
    first = lines[0]
    content = ''.join(lines[1:])

    def at(action, target):
        return {
            'action': action,
            'target': target,
            'content': content,
            'indent': indent,
            'line': line,
        }


    if first.startswith('# content of'):
        target = first.strip().split()[-1]
        return at('write', target)
    elif first[0] == '$':
        cmd = first[1:].strip()
        return at('shell', cmd)

    return at(None, first)


def actions_of(file):
    lines = file.read().splitlines(True)
    for indent, line, data in blocks(lines):
        mapping = classify(lines=data, indent=indent, line=line)
        if mapping['action']: # None if no idea
            yield mapping


def do_write(tmpdir, target, content):
    #XXX: insecure
    targetfile = tmpdir.join(target).write(content)


def do_shell(tmpdir, target, content):
    proc = subprocess.Popen(
        target,
        shell=True,
        cwd=str(tmpdir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate()
    if out != content: #XXX join with err?
        import difflib
        differ = difflib.Differ()
        outl = out.splitlines(True)
        contl = content.splitlines(True)
        result = differ.compare(contl, outl)
        print ''.join(result)
        return out


def execute(file, tmpdir):
    needed_updates = []
    for m in actions_of(file):
        print m['action'], repr(m['target'])

        method = globals()['do_' + m['action']]
        new_content = method(tmpdir, m['target'], m['content'])
        if new_content:
            m['new_content'] = new_content
            needed_updates.append(m)
    return needed_updates


def main():
    options = parser.parse_args()
    import py

    for name in options.files:
        tmpdir = py.path.local.make_numbered_dir(prefix='doc-exec-')
        p = py.path.local(name)
        print 'checking', name
        execute(
            file = p,
            tmpdir = tmpdir,
        )
        


if __name__=='__main__':
    main()
