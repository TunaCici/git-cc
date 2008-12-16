from common import *
from os.path import join, dirname

class Status:
    def __init__(self, files):
        self.setFile(files[0])
    def setFile(self, file):
        self.file = file
    def cat(self):
        blob = git_exec(['cat-file', 'blob', getBlob(self.id, self.file)])
        write(join(CC_DIR, self.file), blob)
    def stageDirs(self, t):
        dir = dirname(self.file)
        dirs = []
        while not exists(join(CC_DIR, dir)):
            dirs.append(dir)
            dir = dirname(dir)
        self.dirs = dirs
        t.stage(dir)
    def commitDirs(self, t):
        while len(self.dirs) > 0:
            dir = self.dirs.pop();
            t.mkdirelem(dir)

class Modify(Status):
    def stage(self, t):
        t.stage(self.file)
    def commit(self, t):
        self.cat()

class Add(Status):
    def stage(self, t):
        self.stageDirs(t)
    def commit(self, t):
        self.commitDirs(t)
        self.cat()
        t.mkelem(self.file)

class Delete(Status):
    def stage(self, t):
        t.stage(dirname(self.file))
    def commit(self, t):
        # TODO Empty dirs?!?
        cc_exec(['rm', self.file])

class Rename(Status):
    def __init__(self, files):
        self.old = files[0]
        self.new = files[1]
        self.setFile(self.new)
    def stage(self, t):
        t.stage(dirname(self.old))
        t.stage(self.old)
        self.stageDirs(t)
    def commit(self, t):
        self.commitDirs(t)
        cc_exec(['mv', '-nc', self.old, self.new])
        t.checkedout.remove(self.old)
        t._add(self.new)
        self.cat()