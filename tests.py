from phlibs.jqueue import Job
from phlibs.modules import Module
from phlibs.host import HostList

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
    # Dummy class
    i = DummyInput(['1.1.1.1'])
    # Dummy module - does nothing
    m = Module({})
    hl = HostList(i, [m])
    return hl

def dummy_function(a,b):
    print(a+b)

if __name__ == '__main__':
    hl = InstantiateHostList()
    j = Job(hl.run_all_hosts, ())
    j.Run()