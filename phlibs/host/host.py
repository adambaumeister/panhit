import os
import json
from phlibs.jqueue import JobQueue, Job


class HostList:
    """
    List of Host Entries
    """

    def __init__(self, input=None, mods_enabled=None, db=None, tags_policy=None):
        """
        Instantiate a host list based on a given input type.
        :param input: Class of type Input but can be anything with a List() function
        :param mods_enabled: Discovery modules to use
        :param db (optional): Run database. If provided, enables async processing./
        :param tag_policy (optional): Tag configuration.
        """
        self.mods_enabled = mods_enabled
        self.tags_policy = tags_policy

        if input:
            self.hosts = self.hosts_from_list(input.List())
        else:
            self.hosts = []
        self.db = db
        self.index = []

    def hosts_from_list(self, host_dicts):
        hosts = []
        for hd in host_dicts:
            if 'ip' not in hd:
                raise ValueError("Missing field ip in host list.")

            h = Host(ip=hd['ip'], mods_enabled=self.mods_enabled, tag_policy=self.tags_policy)
            h.add_data_dict(hd)
            hosts.append(h)

        return hosts

    def get_all_hosts(self):
        if self.db:
            index = self.db.get("index")
            hosts = []
            for hid in index:
                host_json = self.db.get(hid)
                h = unpickle_host(host_json)
                hosts.append(h)

            self.hosts = hosts
            return hosts

        return self.hosts

    def run_all_hosts(self, jq=None):
        """
        Run all the modules for all hosts
        if a JobQueue object is specified, this will run async
        :param jq: JobQueue instance
        """
        done = 0
        total = len(self.hosts)
        if self.db:
            # Set the path to store this run
            self.db.update_path(jq.get_id())
            # Pass the db object to the JsonDB so it can write
            jq.set_db(self.db)

            for h in self.hosts:
                # Create a uid for each host
                hid = self.db.make_id()
                self.index.append(str(hid))

                h.set_db(self.db)
                h.set_id(hid)
                j = Job(h.run_all_mods, (hid,))
                jq.add_job(j)

            self.db.write_id("index", self.index)

            jq.empty()

            return

        for h in self.get_all_hosts():
            h.run_all_mods()
            done = done + 1
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

    def __init__(self, ip, mods_enabled=None, tag_policy=None):
        """
        Create a new host object.
        :param ip: IP address of the host - required.
        :param mods: Mods to enable for this host.
        """
        self.id = None
        self.mods_enabled = mods_enabled
        self.ip = ip
        self.result = {}
        self.attributes = {}
        self.tag = ''
        self.db = None
        self.tag_policy = []
        if tag_policy:
            self.tag_policy = tag_policy

    def match_tag(self):
        for t in reversed(self.tag_policy):
            if 'match_any' in t:
                match = True
            else:
                match = True
                for match_attr, match_value in t['match'].items():
                    r = self.compare_attr(match_attr, match_value)
                    if not r:
                        match = False

            if match:
                self.set_tag(t['name'])

    def set_db(self, db):
        self.db = db

    def set_id(self, hid):
        """
        Set the Host ID, which is used in various database calls
        :param hid: (str) UID
        """
        self.id = hid

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

    def run_all_mods(self, hid):
        """
        Run all mods and enrich this object with the results
        """
        # Run the mods
        for mod in self.mods_enabled:
            data = mod.Get(self)
            self.result[mod.get_name()] = data

        # Tag based on said mod response
        if self.tag_policy:
            self.match_tag()

        # Optionally, write to the database.
        if self.db:
            self.db.write_id(str(hid), self.pickle())

    def dump_mod_results(self):
        print(self.result)

    def dump_attributes(self):
        return (self.attributes)

    def pickle(self):
        d = {
            'id': str(self.id),
            'attributes': self.attributes,
            'mods_enabled': self.result
        }
        return d

    def unpickle(self, host_json):
        self.id = host_json['id']
        self.attributes = host_json['attributes']
        self.result = host_json['mods_enabled']

    def compare_attr(self, attr_name, attr_value):
        for mod, results in self.result.items():
            if attr_name in results:
                if attr_value == "exists":
                    return True
                elif ">" in attr_value:
                    v = attr_value[1:]
                    if results[attr_name] > int(v):
                        return True
                elif attr_value == results[attr_name]:
                    return True

                return False

        return False

    def set_tag(self, tag):
        self.tag = tag
        self.attributes['tag'] = tag
