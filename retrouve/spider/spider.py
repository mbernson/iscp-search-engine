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

            if not self.can_crawl_url(url):
                self.jobs.clear_job(job)
                return False

            print("Downloading URL '%s'" % url)
            response = self.fetch(url)
            print("Got response code %s" % response.status_code)

            doc = Document.from_response(response, url)
            doc.purge_docs_for_url(url)
            doc.insert()

            if doc.can_index:
                print("Indexing...")
                doc.add_urls_to_index()
                doc.create_excerpts()

            # Schedule the job to be repeated after some period of time
            recrawl_at = datetime.now() + self.repeat_delta
            self.jobs.reschedule_job(job, recrawl_at)
        except Exception as e:
            # Release the job back on to the queue if an error occurs
            self.jobs.release_job(job)
            raise e

    def can_crawl_url(self, url):
        if url.blacklisted:
            print("Clearing url %s from the job queue because it is blacklisted" % url.id)
            return False

        scheme = url.parts.scheme
        if scheme in ('http', 'https'):
            return True

        print("Clearing url %s from the job queue because I don't understand the scheme '%s'" % (url.id, scheme))
        return False

    def fetch(self, url):
        try:
            return requests.get(url.geturl(), headers=self.headers)
        except requests.exceptions.ConnectionError as e:
            print(e)
            raise Exception("HTTP Connection error, bailing out.")
