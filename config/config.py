from modules import *
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

        # Dictionary of module + options from the configuration file
        self.mod_options = {}
        # Enabled retrieval modules
        self.mods_enabled = []
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
                    print(new_opts)
                mods.append(self.mods_available[mod](new_opts))
            else:
                raise ValueError("{} is not a valid module.".format(mod))


        return mods