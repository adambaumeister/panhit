
class Message:
    def __init__(self):
        pass

    def GetMsg(self):
        pass


class JobStarted(Message):
    def __init__(self):
        super(JobStarted, self).__init__()
        self.jid = ''

    def set_jobid(self, jid):
        self.jid = jid

    def set_status(self, status):
        self.status = status

    def GetMsg(self):
        return {
            "id": self.jid,
            "status": self.status
        }

class JobStatus(Message):
    def __init__(self):
        super(JobStatus, self).__init__()
        self.json_job = {}

    def set_from_json(self, j):
        self.json_job = j

    def GetMsg(self):
        return self.json_job

class JobList(Message):
    def __init__(self):
        super(JobList, self).__init__()
        self.count = 0
        self.result = {}

    def set_from_json(self, j):
        self.count = len(j)
        self.result = j

    def set_table_from_json(self, j):
        fields = []
        rows = []
        for d in j:
            for k in d.keys():
                fields.append(k)

        for d in j:
            row = []
            for k in fields:
                row.append(d[k])
            rows.append(row)

        self.result['fields'] = fields
        self.result['rows'] = rows

    def page(self, page, count):
        rows = self.result['rows']
        idx = int(page)*count
        paged_rows = rows[idx:idx+count]
        self.result['rows'] = paged_rows

    def GetMsg(self):
        return {
            "count": self.count,
            "result": self.result
        }

class ConfigStatus(Message):
    def __init__(self):
        super(ConfigStatus, self).__init__()
        self.status = 1
        self.long_status = ''
        self.name = None

    def set_status(self, status):
        self.status = status

    def set_name(self, name):
        self.name = name

    def set_long_status(self, ls):
        self.long_status = ls

    def GetMsg(self):
        return {
            "status": self.status,
            "result": self.long_status,
            "name": self.name,
        }

class ConfigGet(Message):
    def __init__(self):
        super(ConfigGet, self).__init__()
        self.items = []

    def set_items(self, items):
        self.items = items

    def GetMsg(self):
        return {
            "items": self.items,
        }

class ModuleSpec(Message):
    def __init__(self):
        super(ModuleSpec, self).__init__()
        self.specs = None

    def set_specs(self, specs):
        self.specs = specs

    def GetMsg(self):
        return {
            "module_option_spec": self.specs,
        }