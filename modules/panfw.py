from .mod import Module, ModuleOptions
from panos import Panos

class Panfw(Module):
    """
    Query a host for DNS information.

    Requires
        'ip'
    Produces
        'hostname'
    """
    def __init__(self, mod_opts=None):
        self.module_options = ModuleOptions(
            required_opts=['addr', 'user', 'pw']
        )
        super(Panfw, self).__init__(mod_opts)
        self.name = 'panfw'
        self.module_options.get_opt('addr')

    def Get(self, host):
        return self.data

    def query_arp(self):
        pass