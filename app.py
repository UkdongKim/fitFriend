from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from session import app_session
from datetime import datetime, timedelta



app = Flask(__name__)
app.secret_key = 'moon'
client = MongoClient('15.164.215.62:27017', username='dbadmin', password='admin1234')
db = client.test

app.register_blueprint(app_session) # blueprint 등록


@app.route('/')
def hello_world():  # put application's code here
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

    return render_template("index.html", sessionDataList=result)

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

# 월요일과 일요일 구하기
def get_start_end_of_week(current_date):
    # 현재 날짜를 기준으로 해당 주의 시작을 찾음
    start_of_week = current_date - timedelta(days=current_date.weekday())
    # 현재 날짜를 기준으로 해당 주의 끝을 찾음 (일요일)
    end_of_week = start_of_week + timedelta(days=6)

    return start_of_week.strftime("%Y%m%d"), end_of_week.strftime("%Y%m%d")

if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)