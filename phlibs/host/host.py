import os
import json
from phlibs.jqueue import JobQueue, Job

class HostList:
    """
    List of Host Entries
    """
    def __init__(self, input, mods_enabled=None, db=None):
        """
        Instantiate a host list based on a given input type.
        :param input: Class of type Input but can be anything with a List() function
        :param mods_enabled: Discovery modules to use
        :param db (optional): Run database. If provided, enables async processing./
        """
        self.mods_enabled = mods_enabled
        self.hosts = self.hosts_from_list(input.List())
        self.db = db


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
        if self.db:
            hosts = []
            j = self.db.get_all()
            for host_json in j:
                h = unpickle_host(host_json)
                hosts.append(h)

            self.hosts = hosts
            return hosts

        return self.hosts

    def run_all_hosts(self):
        done = 0
        total = len(self.hosts)
        if self.db:

            jq = JobQueue()
            self.db.update_path(jq.get_id())
            for h in self.hosts:
                h.set_db(self.db)
                j = Job(h.run_all_mods, ())
                jq.add_job(j)

            jq.empty()

            return

        for h in self.get_all_hosts():
            h.run_all_mods()
            done = done+1
            print("Done {}/{}".format(done, total))

def unpickle_host(host_json):
    host = Host(host_json['attributes']['ip'])
    host.unpickle(host_json)
    return host

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
        self.tag = ''

    def set_db(self, db):
        self.db = db


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

        if self.db:
            self.db.write(self.pickle())

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

    def unpickle(self, host_json):
        self.attributes = host_json['attributes']
        self.result = host_json['mods_enabled']

    def compare_attr(self, attr_name, attr_value):
        for mod, results in self.result.items():
            if attr_name in results:
                if attr_value == "exists":
                    return True
                elif ">" in attr_value:
                    v = attr_value[1:]
                    if int(v) > results[attr_name]:
                        return True
                elif attr_value == results[attr_name]:
                    return True

                return False

        return False

    def set_tag(self, tag):
        self.tag = tag
        self.attributes['tag'] = tag
