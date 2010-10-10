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
            mapping = classify(lines=data, indent=indent, line=line)
            if mapping['action']: # None if no idea
                yield mapping


    def run(self):
        needed_updates = []
        for m in self.read_actions():
            print m['action'], repr(m['target'])

            method = getattr(self, 'do_' + m['action'])
            new_content = method(m['target'], m['content'])
            if new_content:
                m['new_content'] = new_content
                needed_updates.append(m)
        return needed_updates

    def do_write(self, target, content):
        #XXX: insecure
        self.tmpdir.join(target).write(content)

    def do_shell(self, target, content):
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
            return out



def main():
    import py
    import sys

    for name in sys.argv[1:]:
        tmpdir = py.path.local.make_numbered_dir(prefix='doc-exec-')
        p = py.path.local(name)
        print 'checking', name
        executor = Executor(
            file = p,
            tmpdir = tmpdir,
        )
        executor.run()



if __name__ == '__main__':
    main()
