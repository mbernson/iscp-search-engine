from flask import Flask, render_template, request
from retrouve.database.job import Job
from retrouve.database.url import Url

app = Flask(__name__, static_folder='static', static_url_path='')


@app.route("/")
def search():
    return render_template('search.html')


@app.route("/search")
def results():
    query = request.args.get('q', '')
    result = {
        'title': 'A quick brown fox',
        'url': 'http://example.com/',
        'excerpt': 'The quick brown fox <mark>jumped</mark> over the lazy dog. [...]'
    }
    results = [result, result, result, result, result, result, result]
    return render_template('results.html', query=query, results=results)


@app.route("/add_url", methods=['POST', 'GET'])
def add_url():
    if request.method == 'POST':
        url = Url.from_url(request.form['url'])
        return render_template('add_url.html', added=url.insert(), url=url)
    else:
        return render_template('add_url.html', added=False)
