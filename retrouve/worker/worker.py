from retrouve.database.job import JobRepository


class Worker:
    """
    Base class for worker programs which perform tasks
    from the job queue.
    """

    def __init__(self):
        self.jobs = JobRepository()

    def work(self):
        """
        Perform a single unit of work.
        :return:
        """
        pass
