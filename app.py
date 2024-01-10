from datetime import timedelta, datetime
import hashlib
import json
from flask import Flask, flash, render_template, request, redirect, url_for, session, jsonify, make_response
from pymongo import MongoClient
from session import app_session
from bson import json_util
from flask_jwt_extended import JWTManager, decode_token
import jwt


app = Flask(__name__)
app.secret_key = 'MOONUNG'


SECRET_KEY = 'MOONUNG'

jwt_manager = JWTManager(app)

client = MongoClient('15.164.215.62:27017', username='dbadmin', password='admin1234')
db = client.test

app.register_blueprint(app_session) # blueprint 등록

def parse_json(data):
    return json.loads(json_util.dumps(data))

# 메인 페이지
@app.route('/')
def hello_world():
    token = request.cookies.get('token')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        print(payload['username'])
        print(payload['password'])
        user_info = db.users.find_one({"name": payload['username']})
        return render_template('index.html', username=user_info['name'], gender=user_info['gender'])
    except jwt.ExpiredSignatureError:
        flash("로그인 시간이 만료되었습니다. 다시 로그인 해")
        response = make_response(redirect(url_for("login")))
        response.set_cookie('token', '', expires=0)   # 쿠키 삭제
        return response
    except jwt.exceptions.DecodeError:
        flash("로그인 정보가 존재하지 않습니다. 다시 로그인 해주세요.")
        response = make_response(redirect(url_for("login")))
        response.set_cookie('token', '', expires=0)   # 쿠키 삭제
        return response

# 로그인
@app.route('/login', methods=['GET'])
def login():
    token = request.cookies.get('token')
    if token:
        return redirect(url_for('hello_world'))
    
    return render_template('login.html')

# 로그인 성공 시
@app.route('/loginOk', methods=['POST'])
def loginOk():
    username = request.form['username']
    password = request.form['password']

    pwHash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    check = db.users.find_one({'name' : username, 'password': pwHash})

    if check is not None:
        payload = {
            'username' : username,
            'password' : pwHash,
            'exp' : datetime.utcnow() + timedelta(seconds=60)
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        response = make_response(redirect(url_for('hello_world')))
        response.set_cookie('token', token)
        return response
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
        return render_template('login.html')
    
    elif username != None and gender != None and password != None and password == passwordcheck :
        pwHash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        db.users.insert_one({'name': username, 'password': pwHash, 'gender': gender})
        print('회원가입 성공')
        return render_template('login.html')
    
# 가이드 이동
@app.route('/guide')
def guide():
    return render_template('guide.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)