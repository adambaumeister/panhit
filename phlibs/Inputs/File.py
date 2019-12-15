import json
from .Input import Input
from phlibs.modules import ModuleOptions, ModuleOption


class ListInput(Input):
    def __init__(self, mod_opts=None):

        data_option = ModuleOption('data')
        data_option.required = True
        self.module_options = ModuleOptions([data_option])

        super(ListInput, self).__init__(mod_opts)

        self.pretty_name = "Manual"

    def List(self):
        self.data = self.module_options.get_opt('data')
        return self.data

    def Output(self):
        pass

class FileInput(Input):
    def __init__(self, mod_opts=None):


        data_option = ModuleOption('location')
        data_option.required = True
        self.module_options = ModuleOptions([data_option])

        super(FileInput, self).__init__(mod_opts)
        self.pretty_name = "File"

        pass

    def List(self):
        source = self.module_options.get_opt('source')

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