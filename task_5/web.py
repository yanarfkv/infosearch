from flask import Flask, request, render_template
from main import vector_search

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    query = ""
    if request.method == 'POST':
        query = request.form['query']
        results = vector_search(query)
    return render_template('index.html', query=query, results=results)


if __name__ == '__main__':
    app.run(debug=True)
