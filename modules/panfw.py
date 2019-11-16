from .mod import Module, ModuleOptions
from panos import Panos
from xml.etree import ElementTree
import ipaddress
import time

MAX_REPORT_QUERIES=20

APPS_BY_IP_REPORT="""
        <type>
          <trsum>
            <sortby>sessions</sortby>
            <aggregate-by>
              <member>app</member>
            </aggregate-by>
            <values>
              <member>sessions</member>
            </values>
          </trsum>
        </type>
        <period >{}</period>
        <topn>10</topn>
        <topm>10</topm>
        <caption >test</caption>
        <query>addr.src in {}</query>

"""

class Panfw(Module):
    """
    Query a PANOS Firewall for host information.
    """
    def __init__(self, mod_opts=None):
        """
        Initialize an instance of the panfw module.
        """
        self.module_options = ModuleOptions(
            required_opts=['addr', 'user', 'pw'],
            optional_opts=['xpath', 'report_interval']
        )
        super(Panfw, self).__init__(mod_opts)
        self.name = 'panfw'
        self.module_options.get_opt('addr')

        self.arp_cache = {}
        self.route_cache = None
        self.panos = None

    def connect_if_not(self):
        if not self.panos:
            panos = Panos(addr=self.module_options.get_opt('addr'),
                          user=self.module_options.get_opt('user'),
                          pw=self.module_options.get_opt('pw'),
                          )
            self.panos = panos
            return panos
        else:
            return self.panos

    def List(self):
        """
        Retrieve a HostList from this device.
        :return: HostList
        """
        panos = self.connect_if_not()

        params = {
            "type": "config",
            "action": "get",
            "xpath": self.module_options.get_opt('xpath'),
        }

        r = panos.send(params=params)
        host_dict = self.parse_addresses(r.content)
        return host_dict

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

        panos = self.connect_if_not()

        report_interval = self.module_options.get_opt("report_interval")
        if not report_interval:
            report_interval = "last-24-hrs"

        report_spec = APPS_BY_IP_REPORT.format(report_interval, host.ip)
        report_result  = self.run_report(panos, report_spec)

        # If there's a result in the cache
        if len(data.keys()) > 0:
            data.update(report_result)
            return data
        # If there isn't, but the caches are set, then assume there never will be
        elif len(self.arp_cache.keys()) > 0:
            data.update(report_result)
            return data

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

        self.arp_cache = arp_table

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

        data.update(report_result)

        return data

    def Output(self, host_list):
        """
        Output method for this class allows tagging of address objects
        """
        panos = self.connect_if_not()
        xpath = self.module_options.get_opt('xpath')
        address_xpath = xpath + "/address"
        tag_xpath = xpath + "/tag"

        element = """
        <entry name="{}">
            <tag><member>{}</member></tag>
        </entry>
        """
        tag_element = """
        <entry name="{}">
            <comments>Automatically added.</comments>
        </entry>
        """
        tags = set()
        elements = []
        for host in host_list.get_all_hosts():
            new_element = element.format(host.attributes['name'], host.tag)
            elements.append(new_element)
            tags.add(host.tag)

        tag_elements = []
        for tag in tags:
            tag_elements.append(tag_element.format(tag))

        # First we add the tags
        self.send_objects(panos, tag_elements, tag_xpath)
        self.send_objects(panos, elements, address_xpath)


    def send_objects(self, panos, elements, xpath):
        print(xpath, elements)
        params = {
            "type": "config",
            "action": "set",
            "xpath": xpath,
            "element": "".join(elements),
        }
        r = panos.send(params)
        print(r.content)
        result = panos.check_resp(r)
        if not result:
            print("Error adding elements.")

    def route_lookup(self, ip, route_table):
        longest_match = 0
        matched_routes = []
        best_route = {}
        for vr, table in route_table.items():
            for subnet, route in table.items():
                net = ipaddress.ip_network(subnet)
                if "/" in ip:
                    addr = ipaddress.ip_network(ip, strict=False)
                else:
                    addr = ipaddress.ip_address(ip)

                if addr in net:
                    if net.prefixlen >= longest_match:
                        matched_routes.append(route)
                if addr == net:
                    matched_routes.append(route)

        for route in matched_routes:
            if 'C' in route['flags']:
                best_route = route
            else:
                if not best_route:
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

    def parse_addresses(self, data):
        root = ElementTree.fromstring(data)
        table = []

        # Get the entries
        entries = root.findall("./result/address/entry")

        for entry in entries:
            e = {}
            name = entry.attrib['name']
            ipattr = entry.find("./ip-netmask")
            if ipattr is not None:
                ip = ipattr.text
                e['ip'] = ip
                e['name'] = name
                table.append(e)

        return table

    def parse_route_response(self, data):
        root = ElementTree.fromstring(data)
        tables = {}
        # Get the entries
        entries = root.findall("./result/entry")
        for entry in entries:
            route = {}
            nh = entry.find("./nexthop").text
            flags = entry.find("./flags").text
            vr = entry.find("./virtual-router").text
            dest = entry.find("./destination").text
            interface = entry.find("./interface").text
            route['nexthop'] = nh
            route['destination'] = dest
            route['interface'] = interface
            route['vr'] = vr
            route['flags'] = flags
            if vr not in tables:
                tables[vr] = { dest: route }
            else:
                tables[vr][dest] = route

        return tables

    def run_report(self, panos, report_spec):

        data = {}

        # We grab apps seen for this host in the last 24hrs
        r = panos.send(params={
            "type": "report",
            "reporttype": "dynamic",
            "reportname": "api-dynamic",
            "cmd": report_spec,
        })

        root = ElementTree.fromstring(r.content)
        job = root.find("./result/job")

        js = "ACT"
        run = 0
        while "ACT" in js:
            if run > MAX_REPORT_QUERIES:
                return data
            r = panos.send(params={
                "type": "report",
                "action": "get",
                "job-id": job.text,
            })
            root = ElementTree.fromstring(r.content)
            status = root.find("./result/job/status")
            js = status.text
            result = root
            time.sleep(1)
            run = run+1

        report = result.find("./result/report")
        entries = report.findall("./entry")
        apps = []
        for e in entries:
            app = e.find("./app")
            apps.append(app.text)

        data['apps_seen'] = len(apps)
        data['apps'] = ",".join(apps)
        return data




    def query_arp(self):
        pass