from phlibs.jqueue import Job
from phlibs.modules import Module
from phlibs.host import HostList
from phlibs.db import JsonDB
from phlibs.config import ConfigFile
from web import DEFAULT_CONFIG_FILE

"""
Test suite
"""
class DummyInput:
    def __init__(self, hosts):
        self.hosts = hosts
        pass

    def List(self):
        host_dicts = []
        for h in self.hosts:
            hd = {
                'ip': h
            }
            host_dicts.append(hd)
        return host_dicts

def InstantiateHostList():
    jdb = JsonDB("database")
    # Dummy class
    i = DummyInput(['1.1.1.1'])
    # Dummy module - does nothing
    m = Module({})
    hl = HostList(i, [m], db=jdb)
    return hl

def dummy_function(a,b):
    print(a+b)

def test_jdb_write_encrypted():
    jdb = JsonDB("database")
    jdb.enable_encryption("spaghetti")
    id = jdb.write({
        "test_key": "test_val"
    })
    r = jdb.get(id)
    print(r)

def test_jdb_write_decrypted():
    jdb = JsonDB("database")
    id = jdb.write({
        "test_key": "test_val"
    })
    r = jdb.get(id)
    print(r)

def test_jdb_decrypt_unencrypted():
    jdb = JsonDB("database")
    id = jdb.write({
        "test_key": "test_val"
    })
    jdb.enable_encryption("spaghetti")
    r = jdb.get(id)
    print(r)


def test_get_tags():
    c = ConfigFile()
    c.load_from_file(DEFAULT_CONFIG_FILE)
    c.tags = ["tes5"]
    t = c.get_tag_policy()
    print(t)

if __name__ == '__main__':
    test_jdb_write_encrypted()
    test_jdb_decrypt_unencrypted()