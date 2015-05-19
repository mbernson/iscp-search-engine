from time import sleep
from retrouve.worker import Worker
import requests


class Spider(Worker):
    def work(self):
        print("Spider at work")

        job = self.take_job_from_database('spider')
        params = job.payload
        url = Url.find(params.url_id)

        response = requests.get(url)
        doc = Document.from_response(response)
        doc.url = url

        return doc.insert()
