import os
import sys
import click
import tempfile
import subprocess
import shutil
import re

from .parse import parse_actions, correct_content
from .actions import ACTIONS


def normalize_content(content, operators):
    lines = content.splitlines(True)
    result = []
    for line in lines:
        for op in operators:
            line = op(line)
        result.append(line)
    return ''.join(result)


def check_file(name, content, tmpdir, normalize):
    needed_updates = []
    for action in parse_actions(content, file=name):
        if 'target' in action:
            click.echo('{action} {target!r}'.format(**action))

        method = ACTIONS[action['action']]
        new_content = method(name, tmpdir, action)
        if new_content:
            action['new_content'] = normalize_content(new_content, normalize)
            needed_updates.append(action)
    return needed_updates


def print_diff(content, out):
    if out != content:
        import difflib
        differ = difflib.Differ()
        outl = out.splitlines(True)
        contl = content.splitlines(True)
        lines = differ.compare(contl, outl)

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


class Substituter(object):
    def __init__(self, match, replace):
        self.match = match
        self.replace = replace

    @classmethod
    def plain(cls, token, replace):
        return cls(
            match=re.escape(token),
            replace=re.escape(replace))

    @classmethod
    def parse(cls, s):
        parts = s.split(s[0])
        assert len(parts) == 4
        return cls(
            match=parts[1],
            replace=parts[2],
        )

    def __call__(self, line):
        return re.sub(self.match, self.replace, line)

    def __repr__(self):
        return '<Substituter {self.match!r} to {self.replace!r}>'.format(
            self=self)




@click.command()
@click.argument('files', nargs=-1)
@click.option('--update', is_flag=True)
@click.option('--normalize', type=Substituter.parse, multiple=True)
def main(files, update, normalize=(), rootdir=None):
    tmpdir = rootdir or tempfile.mkdtemp(prefix='regendoc-exec-')
    total = len(files)
    for num, name in enumerate(files):
        targetdir = os.path.join(tmpdir, '%s-%d' % (
            os.path.basename(name), num))
        with open(name) as fp:
            content = list(fp)
        os.mkdir(targetdir)
        click.secho(
            '#[{num}/{total}] {name} checking'.format(
                num=num+1, total=total, name=name), bold=True)
        updates = check_file(
            name=name,
            content=content,
            tmpdir=targetdir,
            normalize=(Substituter.plain(
                targetdir, '$REGENDOC_TMPDIR'),) + normalize,
        )
        for update in updates:
            if update['content'] is None or update['new_content'] is None:
                continue
            print_diff(update['content'], update['new_content'])
        if update:
            corrected = correct_content(content, updates)
            with open(name, "w") as f:
                f.writelines(corrected)
