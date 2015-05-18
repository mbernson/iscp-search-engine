import sys
sys.path.append('.')  # Python packages are fucking stupid

from time import sleep
from retrouve.worker import Worker

class Spider(Worker):
    def work(self):
        print("Spider at work")
        sleep(1)


if __name__ == "__main__":
    print("Spider starting")
    spider = Spider()

    while True:
        spider.work()
