import logging

from flask import Flask, flash, make_response, redirect, render_template, Blueprint, request, jsonify, json, url_for
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from flask_jwt_extended import JWTManager, decode_token
import jwt

app = Flask(__name__)
#local
client = MongoClient('15.164.215.62:27017', username='dbadmin', password='admin1234')

#aws
# client = MongoClient('localhost:27017', username='dbadmin', password='admin1234')
db = client.test

app_session = Blueprint('app_session', __name__)

SECRET_KEY = 'MOONUNG'


# 세션 생성
@app_session.route('/session', methods=['POST'])
def make_session():
    userName = request.form['userName']
    userId = request.form['userId']
    day = request.form['day']
    date = request.form['date']
    time = request.form['time']
    field = request.form['field']
    max_member = request.form['max_member']
    note = request.form['note']
    show = True

    session = {
        'userName': userName,
        'userId': userId,
        'day': day,
        'date' : date,
        'time': time,
        'field': field,
        'max_member': max_member,
        'show': show,
        'note': note,
        'participants': [
            {'name': userName, 'userId': userId}
        ]
    }
    print(session)

    token = request.cookies.get('token')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"name": payload['username']})
        if user_info is not None:
            db.session.insert_one(session)
            flash('세션이 생성되었습니다!')
            return redirect(url_for('hello_world'))
        else:
            flash("생성할 수 없습니다.")
            return redirect(url_for('hello_world'))
    except jwt.ExpiredSignatureError:
        flash("로그인 시간이 만료되었습니다. 다시 로그인 해주세요.")
        response = make_response(redirect(url_for("login")))
        response.set_cookie('token', '', expires=0)   # 쿠키 삭제
        return response
    except jwt.exceptions.DecodeError:
        flash("로그인 정보가 존재하지 않습니다. 다시 로그인 해주세요.")
        response = make_response(redirect(url_for("login")))
        response.set_cookie('token', '', expires=0)   # 쿠키 삭제
        return response

    # if result.inserted_id:
    #     return jsonify({'success': True, 'message': 'Data inserted success'}), 201
    # else:
    #     return jsonify({'success': False, 'message': 'Failed to insert data'}), 500


# 세션 조회
@app_session.route('/session', methods=['GET'])
def select_session():
    current_date = datetime.now()
    start_of_week, end_of_week = get_start_end_of_week(current_date)

    sessionList = db.session.find({
        'date': {'$gte': start_of_week, '$lte': end_of_week},
        'show': True
    }).sort({
        'day': 1,
        'time': 1
    })

    for i in sessionList:
        print(i)

    return {"result" : "success"}, 200


# 세션 참여 등록
@app_session.route('/session/participate', methods=['POST'])
def participate_session():
    userName = request.form['userName']
    userId = request.form['userId']
    sessionId = request.form['sessionId']

    # 세션아이디 유효성 검사
    try:
        session = db.session.find_one({'_id': ObjectId(sessionId)})
    except:
        return jsonify({'result': 'fail', "msg": "세션아이디 확인 필요"})

    # max인원 확인

    # 필드 값이 배열인 경우 그 배열의 길이 계산
    array_length = len(session['participants'])

    if int(session['max_member']) <= array_length:
        logging.debug('참여인원 만석')
        return jsonify({'result': 'fail', "msg": "참여인원 다 참"})
    else:
        logging.debug('참여인원 여유 있음')

    newItem = {
        "name": userName,
        "userId": userId
    }

    updateResult = db.session.update_one({'_id': ObjectId(sessionId)}, {"$push": {'participants': newItem}})

    # 성공 여부 확인
    if updateResult:
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'fail', "msg": "업데이트 실패"})


# 세션_참여_취소
@app_session.route('/session/quit', methods=['POST'])
def except_session():
    # 추후 jwt 또는 쿠키에서 사용자 정보 가져오기.
    userName = request.form['userName']
    userId = request.form['userId']

    sessionId = request.form['sessionId']

    result = db.session.update_one({'_id': ObjectId(sessionId)}, {"$pull" : {"participants" : {"userId": userId}}})
    return jsonify({'result': 'success'})


#세션 삭제
@app_session.route('/session/<session_id>', methods=['PUT'])
def test_session(session_id):
    # ObjectId로 변환하여 몽고디비 문서를 삭제합니다.
    result = db.session.update_one({'_id': ObjectId(session_id)}, {"$set" : {"show" : False}})
    return jsonify({'result': 'success'})


# 월요일과 일요일 구하기
def get_start_end_of_week(current_date):
    # 현재 날짜를 기준으로 해당 주의 시작을 찾음
    start_of_week = current_date - timedelta(days=current_date.weekday())
    # 현재 날짜를 기준으로 해당 주의 끝을 찾음 (일요일)
    end_of_week = start_of_week + timedelta(days=6)

    return start_of_week.strftime("%Y%m%d"), end_of_week.strftime("%Y%m%d")
