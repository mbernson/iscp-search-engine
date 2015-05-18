from time import sleep
from retrouve.worker import Worker


class Spider(Worker):
    def work(self):
        print("Spider at work")
        sleep(1)
