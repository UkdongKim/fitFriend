from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return render_template("index.html", title = 'hello jinja')

if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)