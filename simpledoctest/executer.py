from simpledoctest.blockread import blocks
from simpledoctest.classify import classify
import subprocess


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

def execute(file, tmpdir):
    needed_updates = []
    for m in actions_of(file):
        print m['action'], repr(m['target'])

        method = globals()['do_' + m['action']]
        new_content = method(tmpdir, m['target'], m['content'])
        if new_content:
            m['new_content'] = new_content
            needed_updates.append(m)
    return needed_updates

class Executor(object):
    def __init__(self, file, tmpdir):
        self.file = file
        self.tmpdir = tmpdir





    def run(self):
        return execute(self.file, self.tmpdir)


