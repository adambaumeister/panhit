import json
import os
import pathlib
import uuid

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

    def update_path(self, d):
        self.path = self.path + os.sep + d
        if not os.path.isdir(self.path):
            print("Creating {}".format(self.path))
            os.mkdir(self.path)

    def write(self, document):
        """
        Write a json document to disk.
        :param document: (dict) Dictionary to write to JSON
        """
        id = self.make_id()
        id = str(id)
        full_path = self.path + os.sep + id + ".json"
        fp = open(full_path, 'w')
        json.dump(document, fp)

    def write_id(self, id, document):
        """
        Same as Write function but allows specifying the document ID
        :param id: (str) document id
        :param document: (dict) Dictionary to write to JSON
        """
        full_path = self.path + os.sep + id + ".json"
        fp = open(full_path, 'w')
        json.dump(document, fp)

    def make_id(self):
        id = uuid.uuid1()
        return id

    def get_all(self):
        documents = []
        for item in os.listdir(self.path):
            fullpath = self.path + os.sep + item
            if os.path.isfile(fullpath):
                fp = open(fullpath)
                j = json.load(fp)
                documents.append(j)
        return documents

    def get(self, id):
        fullpath = self.path + os.sep + id + ".json"
        if os.path.isfile(fullpath):
            fp = open(fullpath)
            j = json.load(fp)
            return j
