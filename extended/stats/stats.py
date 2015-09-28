"""Attempt to run using Flask."""

from flask import Flask

app = Flask("stats")

@app.route('/')
def hello_world():
    return "Hello World!"

@app.route('/result/<username>')
def result(username):
    import views
    from flask import request
    return views.result(request, username)

if __name__ == "__main__":
    app.run(debug=True)
