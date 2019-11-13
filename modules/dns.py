import socket
from .mod import Module

class DNSHost(Module):
    """
    Query a host for DNS information.

    Requires
        'ip'
    Produces
        'hostname'
    """
    def __init__(self, mod_opts=None):
        self.module_options = None
        super(DNSHost, self).__init__(mod_opts)
        self.name = 'dns'

    def Get(self, host):
        data = {}
        try:
            hostname = socket.gethostbyaddr(host.ip)
            data['hostname'] = hostname[0]
        except socket.herror as err:
            data = {}


        return data