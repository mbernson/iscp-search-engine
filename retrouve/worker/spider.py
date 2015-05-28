from retrouve.database.document import Document
from retrouve.database.url import Url
from retrouve.worker.worker import Worker
import requests
from datetime import datetime, timedelta


def can_crawl_url(url):
    """
    Determine whether we are allowed to crawl a certain URL.
    :param url:
    :return boolean:
    """
    if url.blacklisted:
        return False

    scheme = url.getparts().scheme
    if scheme in ('http', 'https'):
        return True

    return False


class Spider(Worker):
    """
    Fetches webpages from the 'spider' queue, and stores a representation
    for our search engine in the database.
    """

    queue = 'spider'
    repeat_delta = timedelta(days=7)
    headers = {
        'user-agent': 'PyBot/1.0'
    }

    def work(self):
        """
        :inheritdoc:
        """
        try:
            job = self.jobs.reserve_job(self.queue)
            if job is False:
                return False

            url = Url.find(job.payload['url_id'])

            if not url or not can_crawl_url(url):
                self.jobs.clear_job(job)
                return False

            response = self.fetch(url)

            doc = Document.from_response(response, url)
            doc.purge_docs_for_url(url)
            doc.insert()

            if doc.can_index:
                doc.discover_urls()
                doc.discover_excerpts()
                doc.discover_images()

            # Schedule the job to be repeated after some period of time
            recrawl_at = datetime.now() + self.repeat_delta
            self.jobs.reschedule_job(job, recrawl_at)
        except Exception as e:
            # Release the job back on to the queue if an error occurs
            self.jobs.release_job(job)
            raise e

    def fetch(self, url):
        """
        Download a URL over the network.
        :param url:
        :return: response || :raise Exception:
        """
        try:
            return requests.get(url.geturl(), headers=self.headers)
        except requests.exceptions.ConnectionError as e:
            print(e)
            raise Exception("HTTP Connection error, bailing out.")
