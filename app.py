from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from session import app_session


app = Flask(__name__)
app.secret_key = 'moon'
client = MongoClient('15.164.215.62:27017', username='dbadmin', password='admin1234')
db = client.test

app.register_blueprint(app_session) # blueprint 등록


@app.route('/')
def hello_world():  # put application's code here
    return render_template("index.html")

# 로그인
@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

# 로그인 성공 시
@app.route('/loginOk', methods=['POST'])
def loginOk():
    username = request.form['username']
    password = request.form['password']

    check = db.users.find_one({'name' : username, 'password': password})

    if check:
        session['name'] = username
        if 'gender' in check:
            session['gender'] = check['gender']
            # session['_id'] = check['_id']
            
        return redirect(url_for('hello_world'))
    else:
        return render_template('login.html')

# 회원가입
@app.route('/join', methods=['POST'])
def join():
    username = request.form['username']
    gender = request.form['gender']
    password = request.form['password']
    passwordcheck = request.form['passwordcheck']

    if username != None and gender != None and password != None and password == passwordcheck :
        db.users.insert_one({'name': username, 'password': password, 'gender': gender})
        print('회원가입 성공')
        return render_template('login.html')
    else:
        print('회원가입 실패')


if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)