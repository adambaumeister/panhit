
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

        if mod_opts:
            if 'name' in mod_opts:
                self.name = mod_opts['name']


    def List(self):
        pass
