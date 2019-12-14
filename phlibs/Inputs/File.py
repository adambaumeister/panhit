import json
from .Input import Input

class ListInput(Input):
    def __init__(self, data):
        super(ListInput, self).__init__()
        self.pretty_name = "Manual"
        self.data = data

    def List(self):
        return self.data

    def Output(self):
        pass

class FileInput(Input):
    def __init__(self, source):
        super(FileInput, self).__init__()

        self.pretty_name = "File"

        self.source = source
        pass

    def List(self):
        source = self.source
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