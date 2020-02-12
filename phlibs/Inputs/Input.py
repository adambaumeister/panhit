class Input:
    """
    Input prototype
    """
    def __init__(self, mod_opts=None):

        self.name = ""
        self.pretty_name = ""
        self.help = ""
        self.image_large = ""
        self.image_small = ""

        self.opts = mod_opts
        if mod_opts:
            if 'name' in mod_opts:
                self.name = mod_opts['name']

        self.parse_options()

    def List(self):
        pass

    def parse_options(self):
        if self.opts:
            # If this module has defined module options
            if self.module_options:
                self.module_options.parse_dict(self.opts)