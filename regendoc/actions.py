import os
import click
import tempfile
import subprocess
import shutil

def write(name, targetdir, action, verbose):
    # XXX: insecure
    if verbose:
        click.echo('write to %(target)s' % action)
    target = os.path.join(targetdir, action['target'])
    targetdir = os.path.dirname(target)
    if not os.path.isdir(targetdir):
        os.makedirs(targetdir)
    with open(target, 'w') as fp:
        fp.write(action['content'])


def shell(name, targetdir, action, verbose):


    if action['cwd']:
        # the cwd option is insecure and used for examples
        # that already have all files in place
        # like an examples folder for example

        src = os.path.join(
            os.path.abspath(
                os.path.dirname(action['file'])),
            action['cwd'])
        targetdir = os.path.join(targetdir, action['cwd'])
        shutil.copytree(src, targetdir)

    if not os.path.isdir(targetdir):
        os.makedirs(targetdir)

    if verbose:
        click.echo('popen %(target)s' % action)
    proc = subprocess.Popen(
        action['target'],
        shell=True,
        cwd=targetdir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0,
    )
    out, err = proc.communicate()
    out = out.decode('utf-8')
    assert not err
    return out



def wipe(name, targetdir, action, verbose):
    if verbose:
        click.secho('wiping targetdir %s of %s' % (targetdir, name), bold=True)
    shutil.rmtree(targetdir)
    os.mkdir(targetdir)


ACTIONS = {
    'shell': shell,
    'wipe': wipe,
    'write': write,
}
