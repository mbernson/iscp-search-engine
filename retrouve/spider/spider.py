from time import sleep
import psycopg2
from retrouve.database.document import Document
from retrouve.database.job import Jobs, Job
from retrouve.database.url import Url
from retrouve.worker import Worker
import requests
from datetime import datetime, timedelta


class Spider(Worker):
    queue = 'spider'

    def __init__(self):
        self.jobs = Jobs()

    def work(self):
        try:
            job = self.jobs.take_job_from_database(self.queue)
            print(job)
            url = Url.find(job['payload']['url_id'])

            print("Downloading URL '%s'" % url)
            response = requests.get(url)
            print("got response code %s" % response.status_code)

            doc = Document.from_response(response, url)
            doc.insert()

            available_at = datetime.now() + timedelta(days=7)
            next_job = Job(queue='spider', payload={'url_id':url.id}, available_at=available_at)
            next_job.insert()
            # doc.add_urls_to_index()
            # doc.create_excerpts()
            # self.jobs.clear_job(job)
            self.jobs.release_job(job)
        except Exception as e:
            # Release the job back on to the queue if an error occurs
            self.jobs.release_job(job)
            raise e
