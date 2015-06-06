import os
import click
import tempfile
import subprocess
import shutil

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
    printdiff(action['content'], out)
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


def printdiff(content, out):
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
