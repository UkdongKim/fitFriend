import json
from flask import Flask, flash, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from session import app_session
from bson import json_util


app = Flask(__name__)
app.secret_key = 'moon'
client = MongoClient('15.164.215.62:27017', username='dbadmin', password='admin1234')
db = client.test

app.register_blueprint(app_session) # blueprint 등록

def parse_json(data):
    return json.loads(json_util.dumps(data))

@app.route('/')
def hello_world():  # put application's code here
    if not session:
        return redirect(url_for('login'))
    
    return render_template("index.html")

# 로그인
@app.route('/login', methods=['GET'])
def login():
    if session:
        return redirect(url_for('hello_world'))
    
    return render_template('login.html')


# 로그인 성공 시
@app.route('/loginOk', methods=['POST'])
def loginOk():
    username = request.form['username']
    password = request.form['password']
    check = db.users.find_one({'name' : username, 'password': password})

    print(check)
    if check:
        session['name'] = username
        session['gender'] = check['gender']
        session['userid'] = parse_json(check['_id'])
        return redirect(url_for('hello_world'))
    else:
        flash("이름과 비밀번호를 확인해주세요.")
        return render_template('login.html')

# 회원가입
@app.route('/join', methods=['POST'])
def join():
    username = request.form['username']
    gender = request.form['gender']
    password = request.form['password']
    passwordcheck = request.form['passwordcheck']

    existUser = db.users.find_one({'name': username})

    if existUser is not None:
        flash("동일한 이름이 존재합니다.")
    
    elif username != None and gender != None and password != None and password == passwordcheck :
        db.users.insert_one({'name': username, 'password': password, 'gender': gender})
        print('회원가입 성공')
        return render_template('login.html')



if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)