from .mod import Module, ModuleOptions
from panos import Panos
from xml.etree import ElementTree
import ipaddress

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

        self.arp_cache = {}
        self.route_cache = None

    def Get(self, host):
        """
        Retreives ARP/Routing table information for the host to determine reachability
        """
        data = {}
        cache = self.arp_cache
        if host.ip in cache:
            data = cache[host.ip]

        if self.route_cache:
            route = self.route_lookup(host.ip, self.route_cache)
            for k, v in route.items():
                data[k] = v

        if len(data.keys()) >0:
            return data

        panos = Panos(addr=self.module_options.get_opt('addr'),
                      user=self.module_options.get_opt('user'),
                      pw=self.module_options.get_opt('pw'),
                      )

        # First we grab the arp table
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

        # Next, we grab the routing table
        r = panos.send(params={
            "type": "op",
            "cmd": "<show><routing><route></route></routing></show>"
        })
        if not panos.check_resp(r):
            raise ConnectionError("Failed to retrieve response from panfw.")

        route_table = self.parse_route_response(r.content)
        self.route_cache = route_table

        route = self.route_lookup(host.ip, route_table)
        for k, v in route.items():
            data[k] = v
        return data

    def route_lookup(self, ip, route_table):
        longest_match = 0
        best_route = None
        for subnet, route in route_table.items():
            net = ipaddress.ip_network(subnet)
            addr = ipaddress.ip_address(ip)
            if addr in net:
                if net.prefixlen >= longest_match:
                    best_route = route

        return best_route

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

    def parse_route_response(self, data):
        root = ElementTree.fromstring(data)
        table = {}

        # Get the entries
        entries = root.findall("./result/entry")
        for entry in entries:
            route = {}
            nh = entry.find("./nexthop").text
            dest = entry.find("./destination").text
            interface = entry.find("./interface").text
            route['nexthop'] = nh
            route['destination'] = dest
            route['interface'] = interface
            table[dest] = route

        return table


    def query_arp(self):
        pass