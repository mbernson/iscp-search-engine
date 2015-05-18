from time import sleep


class Worker:
    def start(self):
        while True:
            self.work()

    def work(self):
        print("Please implement .work() on your worker")
        sleep(1)
        pass
