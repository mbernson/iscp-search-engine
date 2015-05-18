from time import sleep
from retrouve.worker import Worker


class Indexer(Worker):
    def work(self):
        print("Indexer at work")
        sleep(1)
