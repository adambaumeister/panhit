from multiprocessing import Process

class JobQueue:
    """
    JobQueue represents an ordered list of Job objects

    Job Queue takes new Job requests, schedules them, and performs the heavy lifting of thread management.

    JobQueue can also be used as the API to query job status, delete jobs, etc.
    """
    def __init__(self, db=None):
        """
        Initialize a JobQueue

        :param db: Database, if provided, in which to store job information.
        """

        self.queue = []

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
        p.join()