from datetime import datetime
from retrouve.database.model import Model
import psycopg2
from datetime import datetime
import json


class Job(Model):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'available_at'):
            self.available_at = datetime.now()

    def insert(self):
        cursor = self.db.cursor()
        try:
            dict = self.__dict__.copy()
            dict['payload'] = json.dumps(self.payload)
            cursor.execute(
                "INSERT INTO jobs (queue, payload, available_at) VALUES (%(queue)s, %(payload)s, %(available_at)s)",
                dict)
            self.db.commit()
            cursor.close()
            return cursor.rowcount == 1
        except psycopg2.Error as e:
            self.db.rollback()
            cursor.close()
            print(e)
        return False

    def insert_bare(self, cursor):
        cursor.execute(
            "INSERT INTO jobs (queue, payload, available_at) VALUES (%(queue)s, %(payload)s, %(available_at)s) RETURNING id",
            self.__dict__)
        self.id = cursor.fetchone()['id']


class Jobs(Model):
    def take_job_from_database(self, queue):
        cursor = self.db.cursor()
        try:
            cursor.execute(
                "SELECT * FROM jobs WHERE "
                "reserved = 'f' AND available_at <= NOW() AND queue = %s AND attempts <= 3 "
                "ORDER BY id ASC FOR UPDATE LIMIT 1",
                (queue,))
            attrs = cursor.fetchone()
            if attrs is None:
                raise Exception("No available jobs found. Moving on.")
            job = Job()
            job.__dict__ = attrs
            cursor.execute("UPDATE jobs SET reserved = 't', reserved_at = NOW() WHERE id = %s", (job.id,))
            self.db.commit()
            cursor.close()
            print("reserving job with id %s" % job.id)
            return job
        except Exception as e:
            print(e)
            self.db.rollback()
            cursor.close()
        return False

    def clear_job(self, job):
        cursor = self.db.cursor()
        try:
            cursor.execute("DELETE FROM jobs WHERE id = %s", (job.id,))
            self.db.commit()
            cursor.close()
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
            cursor.execute("UPDATE jobs SET reserved = 'f', attempts = attempts + 1 WHERE id = %s", (job.id,))
            self.db.commit()
            print("releasing job with id %s" % job.id)
            return cursor.rowcount == 1
        except psycopg2.Error as e:
            print(e)
            self.db.rollback()
            cursor.close()
        return False

    def reschedule_job(self, job, crawl_at):
        cursor = self.db.cursor()
        try:
            cursor.execute("UPDATE jobs SET reserved = 'f', reserved_at = null, available_at = %s WHERE id = %s", (crawl_at, job.id,))
            self.db.commit()
            print("rescheduling job with id %s" % job.id)
            return cursor.rowcount == 1
        except psycopg2.Error as e:
            print(e)
            self.db.rollback()
            cursor.close()
        return False
