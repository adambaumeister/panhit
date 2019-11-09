
CACHE_OPT = 'MOD_CACHE'
class ModuleOptions:
    """
    Options available to a module
    """
    def __init__(self, required_opts=None, optional_opts=None):

        # Cache option allows a dict to act as a simple k/v cache
        # Cache is implemented on a per-module basis

        self.REQUIRED = []
        if required_opts:
            self.REQUIRED = required_opts

        self.OPTIONAL = []
        if optional_opts:
            self.OPTIONAL = optional_opts

        self.options = {}

    def parse_dict(self, d):
        for k in self.REQUIRED:
            if k not in d:
                raise ValueError("Invalid module options; missing {}".format(k))
            else:
                self.options[k] = d[k]

        for k in self.OPTIONAL:
            if k in d:
                self.options[k] = d[k]

    def get_opt(self, opt):
        return self.options[opt]

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
