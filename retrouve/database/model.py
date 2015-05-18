import psycopg2
import psycopg2.extras
import dotenv
import os

dotenv.load_dotenv('./.env')


class Model(object):
    db = psycopg2.connect(host=os.environ.get('DB_HOST'), database=os.environ.get('DB_DATABASE'),
                          user=os.environ.get('DB_USERNAME'), password=os.environ.get('DB_PASSWORD'),
                          cursor_factory=psycopg2.extras.RealDictCursor)  # Make the connection return
                                                                          # dictionaries instead of tuples

    def take_job_from_database(self, queue):
        cur = self.db.cursor()
        try:
            cur.execute("SELECT * FROM jobs WHERE reserved = 'f' AND available_at <= NOW() ORDER BY id ASC FOR UPDATE")
            job = cur.fetchone()
            cur.execute("UPDATE jobs SET reserved = 't', reserved_at = NOW() WHERE id = %s", (job['id'],))
            self.db.commit()
            return job
        except psycopg2.Error as e:
            print("An error occurred")
            print(e)
            self.db.rollback()
            cur.close()
        return False
