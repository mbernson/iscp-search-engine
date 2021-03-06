from flask import Flask, render_template, request
from retrouve.database.url import Url
from retrouve.database.query import Query

app = Flask(__name__, static_folder='static', static_url_path='')


@app.route("/")
def search():
    return render_template('search.html')


@app.route("/search")
def results():
    per_page = 50
    query = Query(request.args.get('q', ''))
    page = int(request.args.get('page', 0))
    offset = page * per_page
    return render_template('results.html', query=query.getquery(), results=query.results(offset=offset),
                           elapsed_time=query.elapsed_time, count=query.count(), page=page)


@app.route("/add_url", methods=['POST', 'GET'])
def add_url():
    if request.method == 'POST':
        url = Url(url=request.form['url'])
        return render_template('add_url.html', added=url.insert(), url=url)
    else:
        return render_template('add_url.html', added=None)
