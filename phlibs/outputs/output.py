class Output:
    """
    A module represents a discrete set of tools for enriching a host with additional data
    """
    def __init__(self, opts):
        self.data = {}
        self.opts = opts
        self.parse_options()

        if opts:
            if 'name' in opts:
                self.name = opts['name']


    def get_name(self):
        return self.name

    def Get(self, host):
        pass

    def parse_options(self):
        if self.opts:
            # If this module has defined module options
            if self.module_options:
                self.module_options.parse_dict(self.opts)
