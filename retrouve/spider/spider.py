from time import sleep
import psycopg2
from retrouve.database.document import Document
from retrouve.database.job import Jobs, Job
from retrouve.database.url import Url
from retrouve.worker import Worker
import requests
from datetime import datetime, timedelta
import urllib.robotparser


class Spider(Worker):
    queue = 'spider'
    repeat_delta = timedelta(days=7)
    robot = urllib.robotparser.RobotFileParser()

    def __init__(self):
        self.jobs = Jobs()

    def work(self):
        try:
            job = self.jobs.take_job_from_database(self.queue)
            if job is False:
                return False
            print(job)
            url = Url.find(job.payload['url_id'])

            print("Downloading URL '%s'" % url)
            response = requests.get(url.geturl())
            print("got response code %s" % response.status_code)

            doc = Document.from_response(response, url)
            doc.insert()

            doc.add_urls_to_index()
            # doc.create_excerpts()

            # Schedule the job to be repeated after some period of time
            recrawl_at = datetime.now() + self.repeat_delta
            self.jobs.reschedule_job(job, recrawl_at)
        except Exception as e:
            # Release the job back on to the queue if an error occurs
            self.jobs.release_job(job)
            raise e
