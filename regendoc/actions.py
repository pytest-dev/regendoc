import os
import click
import subprocess
import shutil


def write(name, target_dir, action, verbose):
    # XXX: insecure
    if verbose:
        click.echo('write to %(target)s' % action)
    target = os.path.join(target_dir, action['target'])
    target_dir = os.path.dirname(target)
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)
    with open(target, 'w') as fp:
        fp.write(action['content'])


def process(name, target_dir, action, verbose):
    if action['cwd']:
        # the cwd option is insecure and used for examples
        # that already have all files in place
        # like an examples folder for example
        if action['cwd'] == '.':
            src = os.path.abspath(os.path.dirname(action['file']))

            target_dir = os.path.join(target_dir, 'CWD')
        else:
            src = os.path.join(
                os.path.abspath(os.path.dirname(action['file'])),
                action['cwd'])

            target_dir = os.path.join(target_dir, action['cwd'])

        shutil.copytree(src, target_dir)

    if not os.path.isdir(target_dir):
        os.makedirs(target_dir)

    if verbose:
        click.echo('popen %(target)s' % action)
    process = subprocess.Popen(
        action['target'],
        shell=True,
        cwd=target_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0,
    )
    out, err = process.communicate()
    out = out.decode('utf-8')
    assert not err
    return out


def wipe(name, target_dir, action, verbose):
    if verbose:
        click.secho('wiping targetdir %s of %s' % (target_dir, name),
                    bold=True)
    shutil.rmtree(target_dir)
    os.mkdir(target_dir)


ACTIONS = {
    'shell': process,
    'wipe': wipe,
    'write': write,
}
