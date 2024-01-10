import json
from flask import Flask, flash, render_template, request, redirect, url_for, session, jsonify, make_response
from pymongo import MongoClient
from session import app_session
from datetime import datetime, timedelta
from bson import json_util
import hashlib
from datetime import timedelta, datetime
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

@app.route('/')
def hello_world():  # put application's code here
    token = request.cookies.get('token')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        print(payload['username'])
        print(payload['password'])
        user_info = db.users.find_one({"name": payload['username']})

        current_date = datetime.now()
        start_of_week, end_of_week = get_start_end_of_week(current_date)

        sessionList = db.session.find({
            'day': {'$gte': start_of_week, '$lte': end_of_week},
            'show': True
        }).sort({
            'day': 1,
            'time': 1
        })
        for i in sessionList:
            print(i)
        result = list(sessionList)
        return render_template('index.html', username=user_info['name'], gender=user_info['gender'], sessionDataList=result)
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
        return redirect(url_for('login'))

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
        return redirect(url_for('login'))
    
    elif username != None and gender != None and password != None and password == passwordcheck :
        pwHash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        db.users.insert_one({'name': username, 'password': pwHash, 'gender': gender})
        print('회원가입 성공')
        return redirect(url_for('login'))

# 가이드 이동
@app.route('/guide')
def guide():
    return render_template('guide.html')


# 월요일과 일요일 구하기
def get_start_end_of_week(current_date):
    # 현재 날짜를 기준으로 해당 주의 시작을 찾음
    start_of_week = current_date - timedelta(days=current_date.weekday())
    # 현재 날짜를 기준으로 해당 주의 끝을 찾음 (일요일)
    end_of_week = start_of_week + timedelta(days=6)

    return start_of_week.strftime("%Y%m%d"), end_of_week.strftime("%Y%m%d")

#로그아웃
@app.route('/logout')
def logout():
    # token = request.cookies.get('token')
    flash("로그아웃 되었습니다. 로그인 화면으로 돌아갑니다.")
    response = make_response(redirect(url_for("login")))
    response.set_cookie('token', '', expires=0)   # 쿠키 삭제
    return response

if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)