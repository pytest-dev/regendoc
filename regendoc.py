#!/usr/bin/env python
import os
import click
import tempfile
import subprocess


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
                firstline += 1
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
        try:
            result.append((indent, firstline, items))
        except UnboundLocalError:
            pass
    return result


def correct_content(content, updates):

    lines = list(content)
    for update in reversed(updates):
        line = update['line']
        old_lines = len(update['content'].splitlines())
        indent = ' ' * update['indent']
        new_lines = [indent + _line
                     for _line in update['new_content'].splitlines(1)]
        lines[line + 1:line + old_lines + 1] = new_lines

    return lines


def classify(lines, indent=4, line=None):
    if not lines:
        return {'action': None}
    first = lines[0]
    content = ''.join(lines[1:])

    def at(action, target, cwd=None):
        return {
            'action': action,
            'cwd': cwd,
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
    elif ' $ ' in first:
        cwd, target = first.split(' $ ')
        target = target.strip()
        return at('shell', target, cwd)
    elif not indent and any(x.strip() == '.. regendoc:wipe' for x in lines):
        return {'action': 'wipe'}

    return at(None, first)


def parse_actions(lines):
    for indent, line, data in blocks(lines):
        mapping = classify(lines=data, indent=indent, line=line)
        if mapping['action']:  # None if no idea
            yield mapping


def write(name, tmpdir, action):
    # XXX: insecure
    target = os.path.join(tmpdir, action['target'])
    targetdir = os.path.dirname(target)
    if not os.path.isdir(targetdir):
        os.makedirs(targetdir)
    with open(target, 'w') as fp:
        fp.write(action['content'])


def shell(name, tmpdir, action):
    if action['cwd']:
        cwd = os.path.join(tmpdir, action['cwd'])
    else:
        cwd = tmpdir

    proc = subprocess.Popen(
        action['target'],
        shell=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0,
    )
    out, err = proc.communicate()
    out = out.decode('utf-8')
    assert not err
    if out != action['content']:
        import difflib
        differ = difflib.Differ()
        outl = out.splitlines(True)
        contl = action['content'].splitlines(True)
        result = differ.compare(contl, outl)
        printdiff(result)
        return out


def wipe(name, tmpdir, action):
    click.secho('wiping tmpdir %s of %s' % (tmpdir, name), bold=True)

    for item in os.listdir(tmpdir):
        itempath = os.path.join(tmpdir, item)
        assert os.path.relpath(itempath).startswith(
            os.path.pardir + os.sep)
        os.remove(itempath)


ACTIONS = {
    'shell': shell,
    'wipe': wipe,
    'write': write,
}


def printdiff(lines):
    mapping = {
        '+': 'green',
        '-': 'red',
        '?': 'blue',
    }
    for line in lines:
        color = mapping.get(line[0])
        if color:
            click.secho(line, fg=color, bold=True, nl=False)
        else:
            click.echo(line, nl=False)


def check_file(name, content, tmpdir):
    needed_updates = []
    for action in parse_actions(content):
        if 'target' in action:
            click.echo('{action} {target!r}'.format(**action))

        method = ACTIONS[action['action']]
        new_content = method(name, tmpdir, action)
        if new_content:
            action['new_content'] = new_content
            needed_updates.append(action)
    return needed_updates


@click.command()
@click.argument('files', nargs=-1)
@click.option('--update', is_flag=True)
def main(files, update, rootdir=None):
    tmpdir = rootdir or tempfile.mkdtemp(prefix='regendoc-exec')
    total = len(files)
    for num, name in enumerate(files):
        targetdir = os.path.join(tmpdir, 'doc-exec-%d' % num)
        with open(name) as fp:
            content = list(fp)
        os.mkdir(targetdir)
        click.secho(
            '#[{num}/{total}] {name} checking'.format(
                num=num+1, total=total, name=name), bold=True)
        updates = check_file(name=name, content=content, tmpdir=targetdir)
        if update:
            corrected = correct_content(content, updates)
            with open(name, "w") as f:
                f.writelines(corrected)
