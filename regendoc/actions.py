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
        # the cwd option is insecure and used for examples
        # that already have all files in place
        # like an examples folder for example
        # in future this should probaly copy the tree to the targetdir
        cwd = os.path.join(
            os.path.dirname(action['file']),
            action['cwd'])
    else:
        cwd = targetdir

    if not os.path.isdir(cwd):
        os.makedirs(cwd)

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
