from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('15.164.215.62:27017', username='dbadmin', password='admin1234')
db = client.test


@app.route('/')
def hello_world():  # put application's code here
    db.users.insert_one({'name':'name1', 'age':21})
    return render_template("index.html", title='hello jinja')

# 로그인
@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

# 로그인
@app.route('/loginOk', methods=['POST'])
def loginOk():
    error = None
    username = request.form['username']
    password = request.form['password']
    test_username = '문성준07'
    test_password = '1234'

    print('메소드 들어옴1')

    if username == test_username and password == test_password:
        print('메소드 들어옴2')
        return render_template('index.html')
    else:
        error = '로그인 실패'
        print('메소드 들어옴3')
        return render_template('login.html', error=error)



if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)