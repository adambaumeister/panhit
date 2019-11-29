from phlibs.modules import *
from phlibs.Inputs import *
from phlibs.db import JsonDB
import pathlib
import os
import yaml

DEFAULT_CONFIG_PATH=str(pathlib.Path.home()) + os.sep + "panhit.yaml"

class ConfigFile:
    def __init__(self, path):
        """
        Initialize the yaml/json panhit configuration file.

        The configuration
        :param path: (DEFAULT: ~/panhit.yamlPath to configuration file
        """
        if not path:
            path=DEFAULT_CONFIG_PATH

        self.db = None
        self.tags = []

        # Dictionary of module + options from the configuration file
        self.mod_options = {}
        # Enabled retrieval modules
        self.mods_enabled = []
        self.input = {}
        r = yaml.safe_load(open(path))
        for k,v in r.items():
            self.__setattr__(k, v)

        self.mods_available = {
            'dns': DNSHost,
            'panfw': Panfw,
        }


        pass

    def init_modules(self, mod_opts):
        mods = []
        for mod in self.mods_enabled:
            if mod in self.mods_available:
                new_opts = mod_opts
                if mod in self.mod_options:
                    new_opts.update(self.mod_options[mod])
                mods.append(self.mods_available[mod](new_opts))
            else:
                raise ValueError("{} is not a valid module.".format(mod))


        return mods

    def get_input(self, mod_opts):
        if self.input['type'] == 'file':
            i = FileInput(self.input['location'])
            return i
        elif self.input['type'] == 'panfw':
            mod_opts.update(self.input)
            p = Panfw(mod_opts)
            return p

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
