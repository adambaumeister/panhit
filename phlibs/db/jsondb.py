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
        :param path: Full system path to the datastore, this also becomes the root datastore path
        """
        self.path = path
        self.root = path

    def update_path(self, d):
        """
        Update the current path of the datastore
        """
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

    def get_in_sub(self, id, sub):
        """
        Get a document from a subdir within the db
        :param id: Document ID
        :param sub: Subdirectory name
        :return: document
        """
        fullpath = self.root + os.sep + sub + os.sep + id + ".json"
        if os.path.isfile(fullpath):
            fp = open(fullpath)
            j = json.load(fp)
            return j

    def get_all_in_subdir_sorted(self, doc_id):
        """
        Retrieve a document with the same ID from all the sub-databases (directories within the root)
        :param doc_id: id of document
        :return: (list) Document objects
        """
        docs = []
        for item in os.listdir(self.root):
            fullpath = self.root + os.sep + item + os.sep + doc_id + ".json"
            if os.path.isfile(fullpath):
                fp = open(fullpath)
                j = json.load(fp)
                docs.append(j)

        return docs

    def summary(self):
        """
        Get a summary of all current database objects
        :return: Summary
        """
        subs = []
        latest_time = 0
        latest = None
        for dir in os.listdir(self.root):
            subs.append(dir)
            if self.get_in_sub("jqstatus", dir):
                data = self.get_in_sub("jqstatus", dir)
                time = data['start_time']
                if time > latest_time:
                    latest_time = time
                    latest = dir

        return {
            "latest": latest,
            "sub_count": len(subs),
            "latest_time": latest_time
        }