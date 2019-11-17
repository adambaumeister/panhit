import json
import os
import pathlib

class JsonDB:
    """
    JSONdb is a simple file based JSON data store
    A 'database' represents a parent directory
    """
    def __init__(self, path):
        """
        Initalize a datastore
        :param dbname: Name of the datastore
        :param path: Full system path to the datastore
        """
        self.path = path

    def write(self, document):
        id = self.make_id()
        id = str(id)
        full_path = self.path + os.sep + id + ".json"
        fp = open(full_path, 'w')
        json.dump(document, fp)

    def make_id(self):
        ids = []
        for item in os.listdir(self.path):
            fullpath = self.path + os.sep + item
            if os.path.isfile(fullpath):
                i = item.split(".")[0]
                ids.append(i)

        if len(ids) == 0:
            return 1

        max = sorted(ids, reverse=True)[0]
        return int(max) + 1
