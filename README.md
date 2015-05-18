# Search engine project

Working title: retrouve

## Development

Set up a database:

```
$ createdb search_engine
$ psql search_engine < sql/*.sql
$ cp .env.example .env
$ edit .env # Configure the database connection
```

Create a Python virtual environment:

```
$ [sudo] pip install virtualenv
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

Run one or more processes:

```
$ bin/web # Start the web front end
$ bin/spider # Start a spider process
$ bin/indexer # Start an indexing process
```