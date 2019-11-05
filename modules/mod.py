
class ModuleOptions:
    """
    Options available to a module
    """
    def __init__(self, required_opts=None, optional_opts=None):
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


class Module:
    """
    A module represents a discrete set of tools for enriching a host with additional data
    """
    def __init__(self):
        self.name = 'module'
        self.data = {}
        pass

    def get_name(self):
        return self.name

    def Get(self, host):
        pass

