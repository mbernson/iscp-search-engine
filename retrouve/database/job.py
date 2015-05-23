from datetime import datetime
from retrouve.database.model import Model
import psycopg2
from datetime import datetime

class Job(Model):
    def __init__(self, **kwargs):
        self.available_at = datetime.now()
        super().__init__(**kwargs)

    def payload(self, **args):
        self.payload = args

    def insert(self):
        cursor = self.db.cursor()
        try:
            cursor.execute("INSERT INTO jobs (queue, payload, available_at) VALUES (%(queue)s, %(payload)s, %(available_at)s)",
                        self.__dict__)
            self.db.commit()
            cursor.close()
            return cursor.rowcount == 1
        except psycopg2.Error as e:
            self.db.rollback()
            cursor.close()
            print(e)
        return False


class Jobs(Model):
    def take_job_from_database(self, queue):
        cursor = self.db.cursor()
        try:
            cursor.execute(
                "SELECT * FROM jobs WHERE reserved = 'f' AND available_at <= NOW() AND queue = %s ORDER BY id ASC FOR UPDATE LIMIT 1",
                (queue,))
            attrs = cursor.fetchone()
            job = Job()
            job.__dict__ = attrs
            cursor.execute("UPDATE jobs SET reserved = 't', reserved_at = NOW() WHERE id = %s", (job.id,))
            self.db.commit()
            print("reserving job with id %s" % job.id)
            return job
        except psycopg2.Error as e:
            print(e)
            self.db.rollback()
            cursor.close()
        return False

    def clear_job(self, job):
        cursor = self.db.cursor()
        try:
            cursor.execute("DELETE FROM jobs WHERE id = %s", (job.id,))
            self.db.commit()
            print("clearing job with id %s" % job.id)
            return cursor.rowcount == 1
        except psycopg2.Error as e:
            print(e)
            self.db.rollback()
            cursor.close()
        return False

    def release_job(self, job):
        cursor = self.db.cursor()
        try:
            cursor.execute("UPDATE jobs SET reserved = 'f' WHERE id = %(id)s", job.id)
            self.db.commit()
            print("releasing job with id %s" % job.id)
            return cursor.rowcount == 1
        except psycopg2.Error as e:
            print(e)
            self.db.rollback()
            cursor.close()
        return False
