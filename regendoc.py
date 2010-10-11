#!/usr/bin/python

import argparse
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--update',
                    default=False,
                    action='store_true',
                    help='refresh the files instead of just reporting the difference')
parser.add_argument('files',
                    nargs='+',
                   help='the files to check/update')


def dedent(line, last_indent):
    if last_indent is not None:
        if line[:last_indent].isspace():
            return last_indent, line[last_indent:]
    stripped = line.lstrip(' ')
    return len(line) - len(stripped), stripped


def blocks(lines):
    result = []
    firstline = None
    last_indent = None
    items = []
    for lineno, line in enumerate(lines):

        indent, rest = dedent(line, last_indent)

        if last_indent is None:
            last_indent = indent

        if firstline is None:
            firstline = lineno

        if indent != last_indent:
            if items[0] == '\n':
                del items[0]
                firstline+=1
            if items and items[-1] == '\n':
                del items[-1]
            result.append((last_indent, firstline, items))
            items = [rest]
            last_indent = indent
            firstline = lineno

        else:
            last_indent = indent
            items.append(rest or '\n')

    else:
        result.append((indent, firstline, items))


    return result


def correct_content(content, updates):

    lines = content.splitlines(True)
    for update in reversed(updates):
        line = update['line']
        old_lines = len(update['content'].splitlines())
        indent = ' '*update['indent']
        new_lines = [ indent + _line for _line in update['new_content'].splitlines(1)]
        lines[line+1: line+old_lines+1] = new_lines

    return ''.join(lines)


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


def check_file(file, tmpdir):
    needed_updates = []
    for m in actions_of(file):
        print m['action'], repr(m['target'])

        method = globals()['do_' + m['action']]
        new_content = method(tmpdir, m['target'], m['content'])
        if new_content:
            m['new_content'] = new_content
            needed_updates.append(m)
    return needed_updates


def main(files, should_update, rootdir=None):
    import py
    tw = py.io.TerminalWriter()
    for name in files:
        tw.sep('=', 'checking %s' % (name,), bold=True)
        tmpdir = py.path.local.make_numbered_dir(
            rootdir=rootdir,
            prefix='doc-exec-')
        path = py.path.local(name)
        updates = check_file(
            file = path,
            tmpdir = tmpdir,
        )
        if should_update:
            content = path.read()
            corrected = correct_content(content, updates)
            path.write(corrected)



if __name__=='__main__':
    options = parser.parse_args()
    main(options.files, should_update=options.update)
