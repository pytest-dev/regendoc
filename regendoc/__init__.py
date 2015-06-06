import os
import click
import tempfile
import subprocess
import shutil

from .parse import parse_actions, correct_content
from .actions import ACTIONS


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
        targetdir = os.path.join(tmpdir, '%s-%d' % (
            os.path.basename(name), num))
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
