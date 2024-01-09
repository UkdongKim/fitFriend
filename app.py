from flask import Flask, render_template, request
from pymongo import MongoClient
from session import app_session



app = Flask(__name__)
client = MongoClient('15.164.215.62:27017', username='dbadmin', password='admin1234')
db = client.test

app.register_blueprint(app_session) # blueprint 등록


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
    check = db.users.find_one({'name' : username, 'password': password})

    print('메소드 들어옴1')

    if check:
        print('메소드 들어옴2')
        return render_template('index.html', name=username)
    else:
        error = '로그인 실패'
        print('메소드 들어옴3')
        return render_template('login.html')

@app.route('/join', methods=['POST'])
def join():
    username = request.form['username']
    gender = request.form['gender']
    password = request.form['password']
    print(gender)

    if username != None and gender != None and password != None:
        db.users.insert_one({'name': username, 'password': password, 'gender': gender})
        print('회원가입 성공')
        return render_template('login.html')
    else:
        print('회원가입 실패')


if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)