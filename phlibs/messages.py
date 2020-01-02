
from flask import render_template

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
        self.pages = 1

    def set_from_json(self, j):
        self.count = len(j)
        self.result = j

    def set_table_from_json(self, j):
        fields = []
        rows = []
        for d in j:
            for k in d.keys():
                if k not in fields:
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
            "result": self.result,
            "pages": self.pages
        }

class JobResult(Message):
    """
    ## Need to figure out how to return an ordered list of these unordered objects (for paging purposes)
    """
    def __init__(self):
        super(JobResult, self).__init__()
        self.count = 0
        self.result = {}
        self.pages = 1


    def set_from_json(self, j):
        self.count = len(j)
        self.result = j

    def as_html(self):
        """
        Return the table as a blob of templated html instead of the JSON
        """
        mod_id = 0
        # Munge the data into something that fits into html tables
        for host_data in self.result:
            mod_tables = []

            for mod, mod_data in host_data['mods_enabled'].items():
                mod_headers = []
                mod_row = []

                for k, v in mod_data.items():
                    mod_headers.append(k)

                mod_headers = sorted(mod_headers)
                for k in mod_headers:
                    mod_row.append(mod_data[k])

                mod_table = {
                    "id": mod_id,
                    "name": mod,
                    "headers": mod_headers,
                    "row": mod_row
                }
                mod_tables.append(mod_table)

            mod_id = mod_id + 1

            host_data['mod_tables'] = mod_tables

        return render_template('snippets/results_table.html', hosts=self.result)

    def set_table_from_json(self, j):
        result = []
        for host_ip, host_data in j.items():
            result.append(host_data)

        result = sorted(result, key=lambda d: d['id'])
        self.result = result


    def page(self, page, count):
        rows = self.result
        idx = int(page)*count
        paged_rows = rows[idx:idx+count]
        self.result = paged_rows

    def GetMsg(self):
        self.count = len(self.result)
        return {
            "count": self.count,
            "result": self.result,
            "pages": self.pages
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