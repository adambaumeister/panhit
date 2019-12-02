
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