from multiprocessing import Process
from datetime import datetime

class JobQueue:
    """
    JobQueue represents an ordered list of Job objects

    Job Queue takes new Job requests, schedules them, and performs the heavy lifting of thread management.

    JobQueue can also be used as the API to query job status, delete jobs, etc.
    """
    def __init__(self):
        """
        Initialize a JobQueue object.
        """

        self.queue = []
        now = datetime.now()
        self.id = now.strftime("%d-%m-%Y_%H-%M-%S")
        self.limit = 5
        self.db = None

    def set_db(self, db):
        """
        Takes a Database object and using it to store job information.
        :param db: Panhit DB instance (such as JsonDB)
        """
        self.db = db

    def get_id(self):
        """
        Retrieve the ID of this particular job queue.

        :return: (str) id
        """
        return self.id

    def add_job(self, job):
        self.queue.append(job)

    def empty(self, nowait=False):
        """
        Run all jobs in the queue.
        """
        d = {
            "id": self.id,
            "queued": len(self.queue)
        }
        self.db.write_id('jqstatus', d)

        processes = []
        for j in self.queue:
            if len(processes) >= self.limit:
                for process in processes:
                    process.join()
                    processes = []

            process = j.Run()
            processes.append(process)

        # If nowait is not specified, do not rejoin the processes and run them independently in the bg.
        if not nowait:
            for process in processes:
                process.join()

class Job:
    """
    Job is the spec and status of an individual body of work to be run.
    """
    def __init__(self, func, args):
        self.func = func
        self.args = args

    def Run(self):
        p = Process(target=self.func, args=self.args)
        p.start()
        return p
