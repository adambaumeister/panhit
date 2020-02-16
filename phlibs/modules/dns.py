import socket
from phlibs.modules.mod import Module, ModuleOptions
from phlibs.modules.helpers import is_host

class DNSHost(Module):
    """
    Query a host for DNS information.

    Requires
        'ip'
    Produces
        'hostname'
    """
    def __init__(self, mod_opts=None):
        self.module_options = ModuleOptions([])

        self.name = "dns"
        super(DNSHost, self).__init__(mod_opts)

        self.class_name = 'dns'
        self.pretty_name = "DNS"
        self.image_small = "images/dns.png"
        self.image = "images/dns.png"
        self.type = "dns"

    def Get(self, host):
        data = {}
        if not is_host(host.ip):
            data['hostname'] = "Invalid"
        else:
            try:
                socket.setdefaulttimeout(1)
                hostname = socket.gethostbyaddr(host.ip)
                data['hostname'] = hostname[0]
            except socket.herror as err:
                data = {}
            except socket.gaierror as err:
                data = {}

            return data