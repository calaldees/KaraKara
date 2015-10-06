

class MetaManager(object):

    def __init__(self, path):
        self.path = path
        self.meta = {}

    def get(self, name, file_collection=None):
        if name not in self.meta and file_collection:
            self.meta[name] = MetaFile(name, file_collection)
        return self.meta[name]


class MetaFile(object):

    def __init__(self, name, file_collection=None):
        pass


