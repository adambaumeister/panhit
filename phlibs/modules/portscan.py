import socket
from .mod import Module, ModuleOptions, ModuleOption

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
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = host.ip
        ports = self.module_options.get_opt("ports")
        timeout = self.module_options.get_opt("timeout")

        data = {}
        for port in ports:
            try:
                s.settimeout(timeout)
                s.connect((ip, int(port)))
                s.shutdown(2)
                data[port] = "open"
            except:
                data[port] = "closed"

        return data