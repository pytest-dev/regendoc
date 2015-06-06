import os
import click
import tempfile
import subprocess
import shutil

from .parse import parse_actions, correct_content


def write(name, targetdir, action):
    # XXX: insecure
    target = os.path.join(targetdir, action['target'])
    targetdir = os.path.dirname(target)
    if not os.path.isdir(targetdir):
        os.makedirs(targetdir)
    with open(target, 'w') as fp:
        fp.write(action['content'])


def shell(name, targetdir, action):
    if action['cwd']:
        cwd = os.path.join(targetdir, action['cwd'])
    else:
        cwd = targetdir

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


def wipe(name, targetdir, action):
    click.secho('wiping targetdir %s of %s' % (targetdir, name), bold=True)
    shutil.rmtree(targetdir)
    os.mkdir(targetdir)


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
