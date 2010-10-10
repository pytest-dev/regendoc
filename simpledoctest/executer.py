from simpledoctest.blockread import blocks
from simpledoctest.classify import classify

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
            print action, target

            method = getattr(self, 'do_' + action)
            method(target, content)

    def do_write(self, target, content):
        #XXX: insecure
        self.tmpdir.join(target).write(content)

    def do_exec(self, target, content):
        pass

