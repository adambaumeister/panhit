import json
from .Input import Input
from phlibs.modules import ModuleOptions, ModuleOption


class ListInput(Input):
    def __init__(self, mod_opts=None):

        data_option = ModuleOption('hosts')
        data_option.required = True
        data_option.type_str = "list"
        data_option.nice_name = "Host List"
        self.module_options = ModuleOptions([data_option])

        super(ListInput, self).__init__(mod_opts)

        self.image = "images/file_icon.png"
        self.image_small = "images/file_icon.png"
        self.pretty_name = "Manual"
        self.type = "dict"


    def List(self):
        self.data = self.module_options.get_opt('hosts')
        host_dicts = []
        # Convert into correct format
        for ip in self.data:
            host_dicts.append({ "ip": ip})
        return host_dicts

    def Output(self):
        pass

class FileInput(Input):
    def __init__(self, mod_opts=None):


        data_option = ModuleOption('location')
        data_option.required = True
        data_option.type_str = "file"
        self.module_options = ModuleOptions([data_option])

        super(FileInput, self).__init__(mod_opts)
        self.pretty_name = "File"

        self.image = "images/file_icon.png"
        self.image_small = "images/file_icon.png"

        self.type = "file"


        pass

    def List(self):
        source = self.module_options.get_opt('location')

        host_dicts = []
        try:
            # JSON format
            r = json.load(open(source))
            host_dicts = r['hosts']
            return  host_dicts
        except json.JSONDecodeError:
            pass

        f = open(source)
        lines = f.readlines()
        # CSV format
        keys = lines[0].rstrip().split(",")
        for line in lines[1:]:
            values = line.rstrip().split(",")
            ld = {}
            i=0
            for k in keys:
                ld[k] = values[i]
                i = i+1
            host_dicts.append(ld)

        return host_dicts

    def Output(self):
        """
        File Input type has no matching Output spec.
        """
        pass