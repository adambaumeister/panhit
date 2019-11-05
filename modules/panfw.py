from .mod import Module, ModuleOptions, CACHE_OPT
from panos import Panos
from xml.etree import ElementTree

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
        cache = self.module_options.get_opt(CACHE_OPT)
        if host.ip in cache:
            return cache[host.ip]

        panos = Panos(addr=self.module_options.get_opt('addr'),
                      user=self.module_options.get_opt('user'),
                      pw=self.module_options.get_opt('pw'),
                      )
        r = panos.send(params={
            "type": "op",
            "cmd": "<show><arp><entry name='all'/></arp></show>"
        })
        if not panos.check_resp(r):
            raise ConnectionError("Failed to retrieve response from panfw.")

        arp_table = self.parse_arp_response(r.content)
        if host.ip in arp_table:
            self.data = arp_table[host.ip]

        return self.data

    def parse_arp_response(self, data):
        root = ElementTree.fromstring(data)
        table = {}

        # Get the entries
        entries = root.findall("./result/entries/entry")
        for entry in entries:
            mac = entry.find("./mac").text
            ip = entry.find("./ip").text
            interface = entry.find("./interface").text
            table[ip] = {
                'mac': mac,
                'interface': interface
            }

        return table

    def query_arp(self):
        pass