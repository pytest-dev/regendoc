from simpledoctest.blockread import blocks
from simpledoctest.classify import classify
import subprocess


class Executor(object):
    def __init__(self, file, tmpdir):
        self.file = file
        self.tmpdir = tmpdir



    def read_actions(self):
        lines = self.file.read().splitlines(True)
        for indent, line, data in blocks(lines):
            act = classify(data)
            if act[0]: # 3 times none if no idea
                yield act


    def run(self):
        for action, target, content in self.read_actions():
            print action, repr(target)

            method = getattr(self, 'do_' + action)
            method(target, content)

    def do_write(self, target, content):
        #XXX: insecure
        self.tmpdir.join(target).write(content)

    def do_exec(self, target, content):
        proc = subprocess.Popen(
            target,
            shell=True,
            cwd=str(self.tmpdir),
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

