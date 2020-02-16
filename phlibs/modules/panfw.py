from .mod import Module, ModuleOptions, ModuleOption, ResultSpec, StringResultField, ModuleError
from panos import Panos
from xml.etree import ElementTree
import ipaddress
import time
import urllib3

urllib3.disable_warnings()

MAX_REPORT_QUERIES = 20

APPS_BY_IP_REPORT = """
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
        # Init the output fields
        result_spec = ResultSpec()
        result_spec.new_addr_field("nexthop")
        result_spec.new_addr_field("destination")
        result_spec.new_str_field("interface")
        result_spec.new_str_field("vr")
        result_spec.new_str_field("flags")
        result_spec.new_str_field("apps")
        result_spec.new_str_field("apps_seen")

        # Initialize this modules options
        addr_option = ModuleOption('addr')
        addr_option.nice_name = "Address"
        addr_option.required = True
        addr_option.help = "Address or FQDN of Panorama or NGFW"

        user_option = ModuleOption('user')
        user_option.required = True
        user_option.nice_name = "Username"
        user_option.help = "Must have READ access to objects"

        pw_option = ModuleOption('pw')
        pw_option.required = True
        pw_option.secret = True
        pw_option.nice_name = "Password"

        report_interval = ModuleOption('report_interval')
        report_interval.nice_name = "Reporting interval"
        report_interval.help = "Lower values = faster but less complete results"

        self.module_options = ModuleOptions([
            addr_option, user_option, pw_option,
            report_interval,
        ])
        self.name = "panfw"
        super(Panfw, self).__init__(mod_opts)

        self.result_spec = result_spec

        self.class_name = 'panfw'
        self.pretty_name = "PANOS Device"
        self.image_small = "images/pan-logo-orange.png"
        self.image = "images/pan-logo-orange.png"
        self.type = "panfw"

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
        report_result = self.run_report(panos, report_spec)

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
        tag_color_map = {
            "#9ACB7B": "color13",
            "#DA4302FF": "color1",
            "#FFEA00": "color4",
            "#303F9F": "color26"
        }

        panos = self.connect_if_not()
        xpath = self.module_options.get_opt('xpath')
        address_xpath = xpath + "/address"
        tag_xpath = xpath + "/tag"

        tag_element = """
        <entry name="{}">
            <color>{}</color>
            <comments>Automatically added.</comments>
        </entry>
        """
        tags = {}

        for host in host_list.get_all_hosts():
            if host.tag:
                tag_color = "color11"
                if host.tag["color"]:
                    c = host.tag["color"]
                    if c in tag_color_map:
                        tag_color = tag_color_map[c]

                tag_name = host.tag["name"] + "-ph"
                tags[tag_name] = tag_color

        tag_elements = []
        for tag, color in tags.items():
            tag_elements.append(tag_element.format(tag, color))

        if tag_elements:
            self.send_objects(panos, tag_elements, tag_xpath, 'set')

        for host in host_list.get_all_hosts():
            tag_root = ElementTree.Element("tag")

            # If we are to set a tag
            if host.tag:
                tag_name = host.tag["name"] + "-ph"
                panos_tags = []
                if "panos_tags" in host.attributes:
                    panos_tags = host.attributes["panos_tags"]

                for t in panos_tags:
                    # Exclude ph tags from the list
                    if "-ph" not in t:
                        tag_member = ElementTree.SubElement(tag_root, "member")
                        tag_member.text = t

                tag_member = ElementTree.SubElement(tag_root, "member")
                tag_member.text = tag_name

                full_xpath = address_xpath + "/entry[@name='{}']/tag".format(host.attributes['name'])
                e = ElementTree.tostring(tag_root)
                self.send_object(panos, e, full_xpath, 'edit')

    def send_objects(self, panos, elements, xpath, set_type):
        params = {
            "type": "config",
            "action": set_type,
            "xpath": xpath,
            "element": "".join(elements),
        }
        r = panos.send(params)
        result = panos.check_resp(r)
        if not result:
            print("Error adding elements. {}".format(r.content))

    def send_object(self, panos, element, xpath, set_type):
        params = {
            "type": "config",
            "action": set_type,
            "xpath": xpath,
            "element": element
        }
        r = panos.send(params)
        result = panos.check_resp(r)
        if not result:
            print("Error adding elements. {}".format(r.content))

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
                e['panos_tags'] = []
                tags = entry.findall("./tag/member")
                for t in tags:
                    e['panos_tags'].append(t.text)
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
                tables[vr] = {dest: route}
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

        if not panos.check_resp(r):
            raise ModuleError("Failed to run report!")

        root = ElementTree.fromstring(r.content)
        job = root.find("./result/job")

        if not job.text:
            raise ModuleError("Failed to run report!")

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
            run = run + 1

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

