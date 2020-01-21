import json
import os
import pathlib
import uuid
import pyAesCrypt
import io

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
        self.create_if_not(self.path)
        self.secret = None

    def enable_encryption(self, key):
        self.secret = key

    def disable_encryption(self):
        self.secret = None

    def update_path(self, d):
        """
        Update the current path of the datastore
        """
        self.path = self.path + os.sep + d
        if not os.path.isdir(self.path):
            print("Creating {}".format(self.path))
            os.mkdir(self.path)

    def encrypt(self, str):
        """
        Given an arbtiraty string, encrypt it and return the value.
        :param str: string to encrypt
        :return: encrypted string
        """
        password = self.secret
        bufferSize = 64 * 1024
        # input plaintext binary stream
        fIn = io.BytesIO(str.encode())

        # initialize ciphertext binary stream
        fCiph = io.BytesIO()
        pyAesCrypt.encryptStream(fIn, fCiph, password, bufferSize)
        return fCiph


    def decrypt(self, enc_bytes):
        password = self.secret
        bufferSize = 64 * 1024

        # get ciphertext length
        ctlen = len(enc_bytes)

        # decrypt stream
        fDec = io.BytesIO()
        fIn = io.BytesIO(enc_bytes)
        pyAesCrypt.decryptStream(fIn, fDec, password, bufferSize, ctlen)
        return fDec

    def update_path_nocreate(self, d):
        """
        Update the current path of the datastore
        """
        self.path = self.path + os.sep + d

    def create_if_not(self, p):
        if not os.path.isdir(p):
            print("Creating {}".format(p))
            os.mkdir(p)

    def write(self, document):
        """
        Write a json document to disk.
        :param document: (dict) Dictionary to write to JSON
        """
        id = self.make_id()
        id = str(id)
        self.write_id(id, document)
        return id

    def write_id(self, id, document):
        """
        Same as Write function but allows specifying the document ID
        :param id: (str) document id
        :param document: (dict) Dictionary to write to JSON
        """
        full_path = self.path + os.sep + id + ".json"
        if self.secret:
            fp = open(full_path, 'wb')

            d = json.dumps(document)
            encrypted = self.encrypt(d)
            fp.write(encrypted.getvalue())
        else:
            fp = open(full_path, 'w')

            json.dump(document, fp)

    def make_id(self):
        id = uuid.uuid1()
        return id

    def get_all(self):
        documents = []
        for item in os.listdir(self.path):
            fullpath = self.path + os.sep + item
            j = self.get_fullpath(fullpath)
            documents.append(j)
        return documents

    def get_fullpath(self, full_path):
        if os.path.isfile(full_path):

            if self.secret:
                fp = open(full_path, 'rb')
                # If it's encrypted and we have a secret
                try:
                    r = self.decrypt(fp.read()).getvalue()
                    decoded = r.decode()
                    j = json.loads(decoded)
                # If we have a secret but the file is unencrypted
                except ValueError as e:
                    fp = open(full_path, 'r')
                    try:
                        j = json.load(fp)
                    except UnicodeDecodeError:
                        raise ValueError("Your decryption secret is incorrect or has changed. Your configuration is broken!")
            else:
                fp = open(full_path)
                # If we don't have a secret and the file is unencrypted
                try:
                    j = json.load(fp)
                # Finally, we have no secret and the file is encrypted. This is the only one that should fail!
                except UnicodeDecodeError:
                    raise ValueError("Attempting to decrypt encrypted file without a passphrase. your configuration is broken!")

            return j


    def get(self, id):
        fullpath = self.path + os.sep + str(id) + ".json"
        j = self.get_fullpath(fullpath)
        return j

    def delete_id(self, id):
        """
        Delete a specific document by ID.
        :param id: Document ID
        """
        fullpath = os.path.join(self.path, id + ".json")
        if os.path.isfile(fullpath):
            os.unlink(fullpath)

    def get_in_sub(self, id, sub):
        """
        Get a document from a subdir within the db
        :param id: Document ID
        :param sub: Subdirectory name
        :return: document
        """
        fullpath = self.root + os.sep + sub + os.sep + id + ".json"
        return self.get_fullpath(fullpath)

    def get_all_in_subdir_sorted(self, doc_id, sort_field="start_time", reverse=True, limit=None):
        """
        Retrieve a document with the same ID from all the sub-databases (directories within the root)
        :param doc_id: id of document
        :return: (list) Document objects
        """
        docs = []
        for item in os.listdir(self.root):
            fullpath = self.root + os.sep + item + os.sep + doc_id + ".json"
            j = self.get_fullpath(fullpath)
            docs.append(j)

        sorted_docs = sorted(docs, key=lambda d: d[sort_field])

        if limit:
            if reverse:
                sorted_docs.reverse()

            return sorted_docs[:5]

        # Return the sorted value, sorted by any field in the dictionary (defaults to ID).
        return sorted_docs

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