from phlibs.jqueue import Job
from phlibs.modules import Module
from phlibs.host import HostList
from phlibs.db import JsonDB

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

def test_jdb():
    jdb = JsonDB("database")
    i = jdb.make_id()
    print(i)
    jdb.write({})


if __name__ == '__main__':
    test_jdb()

    hl = InstantiateHostList()

    j = Job(hl.run_all_hosts, ())
    j.Run()