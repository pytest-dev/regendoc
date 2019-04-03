import os
import click
import tempfile
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


def check_file(name, content, tmp_dir, normalize, verbose=True):
    needed_updates = []
    for action in parse_actions(content, file=name):
        method = ACTIONS[action['action']]
        new_content = method(
            name=name,
            target_dir=tmp_dir,
            action=action,
            verbose=verbose)
        if new_content:
            action['new_content'] = normalize_content(new_content, normalize)
            needed_updates.append(action)
    return needed_updates


def print_diff(action):
    content, out = action['content'], action['new_content']
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
        if lines:
            click.secho("$ " + action['target'], bold=True, fg='blue')
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
@click.option('--verbose', default=False, is_flag=True)
def main(files, update, normalize=(), rootdir=None, verbose=False):
    tmpdir = rootdir or tempfile.mkdtemp(prefix='regendoc-exec-')
    total = len(files)
    for num, name in enumerate(files, 1):
        targetdir = os.path.join(tmpdir, '%s-%d' % (
            os.path.basename(name), num))
        with open(name) as fp:
            content = list(fp)
        os.mkdir(targetdir)
        click.secho(
            '#[{num:3d}/{total:3d}] {name}'.format(
                num=num, total=total, name=name), bold=True)
        updates = check_file(
            name=name,
            content=content,
            tmp_dir=targetdir,
            normalize=(
                Substituter(
                    match=re.escape(targetdir),
                    replace='$REGENDOC_TMPDIR',
                ),
                Substituter(
                    match=re.escape(os.getcwd()),
                    replace='$PWD',
                ),
                Substituter(
                    match='at 0x[0-9a-f]+>',
                    replace='at 0xdeadbeef>',
                )
            ) + normalize,
            verbose=verbose,
        )
        for action in updates:
            if action['content'] is None or action['new_content'] is None:
                continue

            print_diff(action)
        if update:
            corrected = correct_content(content, updates)
            with open(name, "w") as f:
                f.writelines(corrected)
