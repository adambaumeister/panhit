import os
import json
class HostList:
    """
    List of Host Entries
    """
    def __init__(self, source, mods_enabled=None):
        self.source = source
        self.mods_enabled = mods_enabled
        if os.path.isfile(source):
            self.hosts = self.parse_file(source)

    def parse_file(self, source):
        host_dicts = []
        try:
            # JSON format
            r = json.load(open(source))
            host_dicts = r['hosts']
            return self.hosts_from_list(host_dicts)
        except json.JSONDecodeError:
            pass

        f = open(source)
        lines = f.readlines()
        # CSV format
        keys = lines[0].rstrip().split(",")
        for line in lines[1:]:
            values = line.rstrip().split(",")
            ld = {}
            i=0
            for k in keys:
                ld[k] = values[i]
                i = i+1
            host_dicts.append(ld)

        return self.hosts_from_list(host_dicts)

    def hosts_from_list(self, host_dicts):
        hosts = []
        for hd in host_dicts:
            if 'ip' not in hd:
                raise ValueError("Missing field ip in host list.")

            h = Host(ip=hd['ip'], mods_enabled=self.mods_enabled)
            h.add_data_dict(hd)
            hosts.append(h)

        return hosts

    def get_all_hosts(self):
        return self.hosts

    def run_all_hosts(self):
        for h in self.get_all_hosts():
            h.run_all_mods()

class Host:
    """
    Main HOST class.

    Hosts contain data per module that is enabled, such as DNS.
    """
    def __init__(self, ip, mods_enabled=None):
        """
        Create a new host object.
        :param ip: IP address of the host - required.
        :param mods: Mods to enable for this host.
        """
        self.mods_enabled = mods_enabled
        self.ip = ip
        self.result = {}
        self.attributes = {}

    def add_data(self, k, v):
        """
        Add a value to this host object.
        :param k: Key
        :param v: Value
        """
        self.attributes[k] = v

    def add_data_dict(self, d):
        for k, v in d.items():
            self.attributes[k] = v

    def run_all_mods(self, mod_opts=None):
        """
        Run all mods and enrich this object with the results
        """
        for mod in self.mods_enabled:
            data = mod.Get(self)
            self.result[mod.get_name()] = data

    def dump_mod_results(self):
        print(self.result)

    def dump_attributes(self):
        return(self.attributes)

    def pickle(self):
        d = {
            'attributes': self.attributes,
            'mods_enabled': self.result
        }
        return d