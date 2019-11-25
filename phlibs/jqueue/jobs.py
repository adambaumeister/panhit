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


    def get_id(self):
        """
        Retrieve the ID of this particular job queue.

        :return: (str) id
        """
        return self.id

    def add_job(self, job):
        self.queue.append(job)

    def empty(self):
        """
        Run all jobs in the queue.
        """
        processes = []
        for j in self.queue:
            if len(processes) >= self.limit:
                for process in processes:
                    print("joining..")
                    process.join()
                    processes = []

            print("running...")
            process = j.Run()
            processes.append(process)

        for process in processes:
            print("joining..")
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
