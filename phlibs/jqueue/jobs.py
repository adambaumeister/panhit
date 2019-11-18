from multiprocessing import Process

class JobQueue:
    """
    JobQueue represents an ordered list of Job objects

    Job Queue takes new Job requests, schedules them, and performs the heavy lifting of thread management.

    JobQueue can also be used as the API to query job status, delete jobs, etc.
    """
    def __init__(self):
        """
        Initialize a JobQueue

        :param db: Database, if provided, in which to store job information.
        """

        self.queue = []

    def add_job(self, job):
        self.queue.append(job)

    def empty(self):
        processes = []
        for j in self.queue:
            process = j.Run()
            processes.append(process)

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
