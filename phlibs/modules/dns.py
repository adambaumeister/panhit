import socket
from .mod import Module, ModuleOptions

class DNSHost(Module):
    """
    Query a host for DNS information.

    Requires
        'ip'
    Produces
        'hostname'
    """
    def __init__(self, mod_opts=None):
        super(DNSHost, self).__init__(mod_opts)

        self.module_options = ModuleOptions([])
        self.name = 'dns'

    def Get(self, host):
        data = {}
        try:
            socket.setdefaulttimeout(1)
            hostname = socket.gethostbyaddr(host.ip)
            data['hostname'] = hostname[0]
        except socket.herror as err:
            data = {}
        except socket.gaierror as err:
            data = {}

        return data