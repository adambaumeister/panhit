from .mod import Module, ModuleOptions
from panos import Panos
from xml.etree import ElementTree

class Panfw(Module):
    """
    Query a PANOS Firewall for host information.
    """
    def __init__(self, mod_opts=None):
        """
        Initialize an instance of the panfw module.
        """
        self.module_options = ModuleOptions(
            required_opts=['addr', 'user', 'pw']
        )
        super(Panfw, self).__init__(mod_opts)
        self.name = 'panfw'
        self.module_options.get_opt('addr')

        self.cache = {}

    def Get(self, host):
        """
        """
        cache = self.cache
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
            data = arp_table[host.ip]

        self.cache = arp_table
        return data

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