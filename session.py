from flask import Flask, render_template, Blueprint, request, jsonify
from pymongo import MongoClient
import uuid
import bson

app = Flask(__name__)
client = MongoClient('15.164.215.62:27017', username='dbadmin', password='admin1234')
db = client.test

app_session = Blueprint('app_session', __name__)


#세션 생성
@app_session.route('/session', methods = ['POST'])
def make_session():

    #해결때까지 주석처리
    # userName = request.form['userName']
    # userId = request.form['userId']
    day = request.form['day']
    time = request.form['time']
    field = request.form['field']
    max_member = request.form['max_member']
    show = True

    session = {
        #위와 동
        # 'userName':userName,
        # 'userId':userId,
        'day':day,
        'time':time,
        'field':field,
        'current_member': 1, #추가했습니다 (사람이 참가를 선택하면 1 오르도록)
        'max_member':max_member,
        'show':show
    }

    result = db.session.insert_one(session)

    if result.inserted_id:
#        return jsonify({'success': True, 'message' : 'Data inserted success'}), 201, 아래의 수정본으로 적용 시 성공 정상적으로 뜸 
        return jsonify({'result':'success', 'message' : 'Data inserted success'}), 201
    else:
        return jsonify({'success': False, 'message': 'Failed to insert data'}), 500


#세션 조회
# @app_session.route('/tile', methods = ['GET'])
# def show_session():

#     tiles = list(db.)




#세션_참여_취소

#세션_삭제

#테스트
@app_session.route('/test')
def hello_world():  # put application's code here
    print('hihi')
    return render_template("index.html", title='goodTest')
