from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('15.164.215.62:27017', username='dbadmin', password='admin1234')
db = client.test


@app.route('/')
def hello_world():  # put application's code here
    db.users.insert_one({'name':'name1', 'age':21})
    return render_template("index.html", title='hello jinja')

if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)