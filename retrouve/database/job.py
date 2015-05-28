from retrouve.database.model import Model
import psycopg2
from datetime import datetime
import json


class Job(Model):
    """
    A single unit of work that can be performed by a worker.
    Every job belongs to one of several queues. It carries a JSON payload.
    Jobs can be scheduled at a certain point in time by setting the available_at timestamp.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'available_at'):
            self.available_at = datetime.now()

    def insert(self):
        cursor = self.db.cursor()
        try:
            cursor.execute(
                "INSERT INTO jobs (queue, payload, available_at) VALUES (%(queue)s, %(payload)s, %(available_at)s)",
                self.serialize())
            self.db.commit()
            cursor.close()
            return cursor.rowcount == 1
        except psycopg2.Error as e:
            self.db.rollback()
            cursor.close()
            print(e)
        return False

    def serialize(self):
        attrs = self.__dict__.copy()
        attrs['payload'] = json.dumps(self.payload)
        return attrs

    def insert_bare(self, cursor):
        cursor.execute(
            "INSERT INTO jobs (queue, payload, available_at) VALUES (%(queue)s, %(payload)s, %(available_at)s) RETURNING id",
            self.self.serialize())
        self.id = cursor.fetchone()['id']


class JobRepository(Model):
    """
    Manages the job queue. Jobs can be reserved, cleared, released or re-scheduled.

    Reserved: the first job that satisfies the queue and time requirements is locked and returned.
    Cleared: the job is removed from the queue.
    Released: the job is put back on the queue, for instance because it has failed.
    Re-scheduled: the job is put back on the queue, to be repeated at some time in the future.
    """

    def __pick_job(self, cursor, queue):
        cursor.execute("SELECT * FROM jobs WHERE "
                       "reserved = 'f' AND available_at <= NOW() AND queue = %s AND attempts <= 3 "
                       "ORDER BY id ASC FOR UPDATE LIMIT 1",
                       (queue,))
        attrs = cursor.fetchone()
        if attrs is None:
            raise Exception("No available jobs found.")
        job = Job(**attrs)
        return job

    def __reserve_job(self, cursor, job):
        cursor.execute("UPDATE jobs SET reserved = 't', reserved_at = NOW() WHERE id = %s", (job.id,))

    def reserve_job(self, queue):
        """
        Reserve the first job in the current queue that is available, and return it.
        :param queue: the queue to use (string)
        :return: Job
        """
        cursor = self.db.cursor()
        try:
            job = self.__pick_job(cursor, queue)
            self.__reserve_job(cursor, job)
            self.db.commit()
            cursor.close()
            print("Reserved job %s" % job.id)
            return job
        except Exception as e:
            print(e)
            self.db.rollback()
            cursor.close()
        return False

    def clear_job(self, job):
        """
        Remove a job from the queue.
        :param: Job
        :rtype: boolean
        """
        cursor = self.db.cursor()
        try:
            cursor.execute("DELETE FROM jobs WHERE id = %s", (job.id,))
            self.db.commit()
            cursor.close()
            print("Cleared job %s with payload %s" % (job.id, json.dumps(job.payload)))
            return cursor.rowcount == 1
        except psycopg2.Error as e:
            print(e)
            self.db.rollback()
            cursor.close()
        return False

    def release_job(self, job):
        """
        Put a job back on the queue. This is often done when the job has failed.
        :param job: Job
        :return: boolean
        """
        cursor = self.db.cursor()
        try:
            cursor.execute("UPDATE jobs SET reserved = 'f', attempts = attempts + 1 WHERE id = %s", (job.id,))
            self.db.commit()
            print("Released job %s" % job.id)
            return cursor.rowcount == 1
        except psycopg2.Error as e:
            print(e)
            self.db.rollback()
            cursor.close()
        return False

    def reschedule_job(self, job, timestamp):
        """
        Put the job back on the queue, to be repeated at some time in the future.
        :param job: Job
        :param timestamp: datetime
        :return: boolean
        """
        cursor = self.db.cursor()
        try:
            cursor.execute("UPDATE jobs SET reserved = 'f', reserved_at = null, available_at = %s WHERE id = %s", (timestamp, job.id,))
            self.db.commit()
            print("Rescheduled job %s" % job.id)
            return cursor.rowcount == 1
        except psycopg2.Error as e:
            print(e)
            self.db.rollback()
            cursor.close()
        return False
