from flask import Flask, render_template, Blueprint
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('15.164.215.62:27017', username='dbadmin', password='admin1234')
db = client.test

app_session = Blueprint('app_session', __name__)


@app_session.route('/test')
def hello_world():  # put application's code here
    print('hihi')
    return render_template("index.html", title='goodTest')
