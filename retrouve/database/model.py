import psycopg2
import dotenv
import os

dotenv.load_dotenv('./.env')

class Model(object):
    db = psycopg2.connect(host=os.environ.get('DB_HOST'), database=os.environ.get('DB_DATABASE'),
                          user=os.environ.get('DB_USERNAME'), password=os.environ.get('DB_PASSWORD'))
