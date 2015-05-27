from time import sleep
from retrouve.database.job import JobRepository


class Worker:
    def __init__(self):
        self.jobs = JobRepository()

    def start(self):
        while True:
            self.work()

    def work(self):
        print("Please implement .work() on your worker")
        sleep(1)
        pass
