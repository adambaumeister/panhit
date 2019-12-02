
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