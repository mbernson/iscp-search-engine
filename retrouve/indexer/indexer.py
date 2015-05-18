import sys
sys.path.append('.')  # Python packages are fucking stupid

from time import sleep
from retrouve.worker import Worker

class Indexer(Worker):
    def work(self):
        print("Indexer at work")
        sleep(1)


if __name__ == "__main__":
    print("Indexer starting")
    indexer = Indexer()

    while True:
        indexer.work()
