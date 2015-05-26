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
    headers = {
        'user-agent': 'PyBot/1.0'
    }

    def __init__(self):
        self.jobs = Jobs()

    def work(self):
        try:
            job = self.jobs.take_job_from_database(self.queue)
            if job is False:
                return False

            url = Url.find(job.payload['url_id'])

            if not url or not self.can_crawl_url(url):
                self.jobs.clear_job(job)
                return False

            response = self.fetch(url)

            doc = Document.from_response(response, url)
            doc.purge_docs_for_url(url)
            doc.insert()

            if doc.can_index:
                doc.add_urls_to_index()
                doc.create_excerpts()
                doc.save_images()

            # Schedule the job to be repeated after some period of time
            recrawl_at = datetime.now() + self.repeat_delta
            self.jobs.reschedule_job(job, recrawl_at)
        except Exception as e:
            # Release the job back on to the queue if an error occurs
            self.jobs.release_job(job)
            raise e

    def can_crawl_url(self, url):
        if url.blacklisted:
            return False

        scheme = url.parts.scheme
        if scheme in ('http', 'https'):
            return True

        return False

    def fetch(self, url):
        try:
            return requests.get(url.geturl(), headers=self.headers)
        except requests.exceptions.ConnectionError as e:
            print(e)
            raise Exception("HTTP Connection error, bailing out.")
