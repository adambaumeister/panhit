from phlibs.modules import *
from phlibs.Inputs import *
from phlibs.outputs import *
from phlibs.db import JsonDB
import pathlib
import os
import yaml

DEFAULT_CONFIG_PATH=str(pathlib.Path.home()) + os.sep + "panhit.yaml"

class ConfigFile:
    def __init__(self):
        """
        Initialize the yaml/json panhit configuration file.

        The configuration
        :param path: (DEFAULT: ~/panhit.yamlPath to configuration file
        """


        self.db = None
        self.configdb = None
        self.tags = []

        # Name identifies this configuration spec
        self.name = None

        # Dictionary of module + options from the configuration file
        self.mod_options = {}
        # Enabled retrieval modules
        self.mods_enabled = []
        self.input = {}
        self.mods_available = {
            'dns': DNSHost,
            'panfw': Panfw,
            'portscan': Portscan,
        }

        # Need to improve this, because these objects require args they must be instantiated
        # Since fixed...
        self.inputs_available = {
            "panfw": PanfwInput(),
            "dict": ListInput(),
            "file": FileInput(),
        }

        self.outputs_available = {
            "panfw": PanfwOutput(),
        }


        pass


    def get_tag_policy(self, tp):
        tags = []
        for tag in tp["tags"]:
            tag_p = self.load_if_str(tag, "tags")
            tags.append(tag_p)

        return tags


    def get_inputs_available(self):
        return self.inputs_available

    def get_mods_available(self):
        mods_available = {}
        for mod_name, mod in self.mods_available.items():
            mods_available[mod_name] = mod()

        return mods_available

    def get_outputs_available(self):
        return self.outputs_available

    def load_from_file(self, path=None):
        if not path:
            path=DEFAULT_CONFIG_PATH

        if os.path.isfile(path):
            r = yaml.safe_load(open(path))
            self.unpickle(r)
            return r

    def unpickle(self, r):
        for k, v in r.items():
            self.__setattr__(k, v)

    def load_if_str(self, data, loc):
        """
        If the passed param data is a str, load it from the database, otherwise, return it directly
        :param data: (str or dict)
        :return: (dict) data
        """
        cdb = self.get_cdb()
        if type(data) is str:
            data = cdb.get_in_sub(data, loc)
            return data
        else:
            return data

    def load_from_spec(self, spec_data):
        """
        Given a spec dict, load all given modules and inputs.
        :param spec_data: (dict)
        :return: ( inputs, modules )
        """
        inputs = []
        mods = []
        tag_policys = []
        output = None
        for input_name in spec_data['inputs']:
            i_data = self.load_if_str(input_name, loc="input")
            i = self.get_input_from_data(i_data)
            inputs.append(i)

        for mod_name in spec_data['modules']:
            mod = self.load_if_str(mod_name, loc="modules")
            mod = self.get_module_from_data(mod)
            mods.append(mod)

        if 'tag_policy' in spec_data:
            tag_policy_ref = spec_data['tag_policy']
            tag_policy = self.load_if_str(tag_policy_ref, "taglist")
            tag_policys = self.get_tag_policy(tag_policy)

        if 'output' in spec_data:
            output = self.load_if_str(spec_data['output'], "output")
            output = self.get_output_from_data(output)

        return inputs, mods, tag_policys, output

    def init_modules(self, mod_opts):
        mods = []
        for mod in self.mods_enabled:
            if mod in self.mods_available:
                new_opts = mod_opts
                if mod in self.mod_options:
                    data = self.load_if_str(self.mod_options[mod], loc="modules")
                    new_opts.update(data)
                mods.append(self.mods_available[mod](new_opts))
            else:
                raise ValueError("{} is not a valid module.".format(mod))


        return mods

    def get_input(self, mod_opts):
        data = self.input
        # If we're passed a string instead of a dictionary, look it up in the database
        data = self.load_if_str(data, "input")

        data.update(mod_opts)

        return self.get_input_from_data(data)

    def get_input_from_data(self, data):
        if data['type'] == 'file':
            i = FileInput(data)
            return i
        elif data['type'] == 'panfw':
            p = PanfwInput(data)
            return p
        elif data['type'] == 'dict':
            l = ListInput(data)
            return l

    def get_output_from_data(self, data):
        if data['type'] == 'panfw':
            p = PanfwOutput(data)
            return p

    def get_module_from_data(self, data):
        if data['type'] in self.mods_available:
            return self.mods_available[data['type']](data)

    def get_output(self, mod_opts):
        if self.output['type'] == 'panfw':
            mod_opts.update(self.output)
            p = Panfw(mod_opts)
            return p
        elif self.output['type'] == 'table':
            output = Table()
            return output


    def get_db(self):
        if self.db:
            if self.db['type'] == 'JsonDB':
                db_path = self.db['path']
                jdb = JsonDB(db_path)
                return jdb

    def get_cdb(self):
        if self.configdb:
            if self.configdb['type'] == 'JsonDB':
                db_path = self.configdb['path']
                jdb = JsonDB(db_path)
                # If we get an environ varaible for secret key we enable encryhption for the config database
                secret = os.getenv("PANHIT_SECRET")
                if secret:
                    jdb.enable_encryption(secret)
                return jdb
