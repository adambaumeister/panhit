

class ModuleOption:
    """
    A single option, passed to a module.
    """
    def __init__(self, name):
        self.name = name
        self.nice_name = name
        self.required = False
        self.secret = False
        # Default option type is str
        self.type = str
        self.type_str = "str"
        self.help = ""

    def spec(self):
        return {
            "name": self.name,
            "nice_name": self.nice_name,
            "required": self.required,
            "secret": self.secret,
            "type": self.type_str,
            "help": self.help,
        }

class ModuleOptions:
    """
    Options available to a module
    """
    def __init__(self, module_options):

        self.module_options = {}
        for option in module_options:
            self.module_options[option.name] = option

        self.options = {}

    def parse_dict(self, d):
        for name, option in self.module_options.items():
            if name not in d:
                if option.required:
                    raise ValueError("Missing module option: {}".format(name))
            else:
                self.options[name] = d[name]


    def get_opt(self, opt):
        if opt not in self.options:
            return None

        return self.options[opt]

    def get_options(self):
        return self.options.keys()

    def get_spec(self):
        spec = []
        for name, option in self.module_options.items():
            spec.append(option.spec())

        return spec

    def get_all_nice(self):
        r = {}
        for name, option in self.module_options.items():
            key = option.nice_name
            if option.secret:
                value = "*******"
            else:
                value = self.get_opt(name)

            r[key] = value
        return r

    def get_all_nice_joined(self):
        r = self.get_all_nice()
        result = []
        for option in r.values():
            if option:
                result.append(option)
        return " • ".join(result)

class Module:
    """
    A module represents a discrete set of tools for enriching a host with additional data
    """
    def __init__(self, opts):
        self.name = 'module'
        self.data = {}
        self.opts = opts
        self.parse_options()

    def get_name(self):
        return self.name

    def Get(self, host):
        pass

    def parse_options(self):
        if self.opts:
            # If this module has defined module options
            if self.module_options:
                self.module_options.parse_dict(self.opts)
