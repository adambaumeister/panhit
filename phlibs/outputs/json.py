
class JsonOutput:
    def __init__(self):
        pass

    def Output(self, host_list):
        data = {}
        for h in host_list.get_all_hosts():
            ip = h.attributes['ip']
            data[ip] = h.pickle()

        return data
