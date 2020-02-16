import socket
from .mod import Module, ModuleOptions, ModuleOption
from phlibs.modules.helpers import is_host

class Portscan(Module):
    """
    Query a host for DNS information.

    Requires
        'ip'
    Produces
        'hostname'
    """
    def __init__(self, mod_opts=None):

        port_option = ModuleOption('ports')
        port_option.nice_name = "Ports"
        port_option.required = True
        port_option.help = "Ports to test"
        port_option.type = list
        port_option.type_str = 'list'


        timeout_option = ModuleOption('timeout')
        timeout_option.nice_name = "Timeout"
        timeout_option.required = False
        timeout_option.help = "Connection Timeout"
        timeout_option.default = 5
        self.module_options = ModuleOptions([
            port_option, timeout_option
        ])

        self.name = "portscan"
        super(Portscan, self).__init__(mod_opts)

        self.class_name = 'portscan'
        self.pretty_name = "Port scan"
        self.image_small = "images/dns.png"
        self.image = "images/dns.png"
        self.type = "portscan"

    def Get(self, host):
        ip = host.ip
        data = {}

        # Don't scan subnet addresses
        if not is_host(ip):
            return data

        ports = self.module_options.get_opt("ports")
        timeout = self.module_options.get_opt("timeout")

        for port in ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                s.settimeout(int(timeout))
                s.connect((ip, int(port)))
                s.shutdown(2)
                data[port] = "open"
            except socket.timeout:
                data[port] = "closed"
            except socket.gaierror:
                data[port] = "host lookup failure"
            except OSError:
                data[port] = "unreachable"

        return data