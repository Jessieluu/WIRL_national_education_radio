# -*- coding: utf-8 -*-
import time
import sys
import math
import random
import json
from io import StringIO
from datetime import datetime, timedelta
from flask import Flask, redirect, url_for, render_template, session, flash, request, jsonify, Response
from flask.ext.login import current_user, login_required, logout_user, login_user
from sqlalchemy import desc
from sqlalchemy import exists
import ast
from NationalEducationRadio.service import get_blueprint
from NationalEducationRadio.service import db
from NationalEducationRadio.models.db.User import User, AccessLevel
from NationalEducationRadio.models.form.LoginForm import LoginForm
from NationalEducationRadio.models.form.RegisterForm import RegisterForm
from NationalEducationRadio.models.units.tools import password_encryption, required_to_flash, audio_upload, \
    parse_question_csv, get_solr_data
from NationalEducationRadio.models.db.Channel import Channel
from NationalEducationRadio.models.db.Audio import Audio
from NationalEducationRadio.models.db.Record import Record
from NationalEducationRadio.models.db.HotPlay import HotPlay
from NationalEducationRadio.models.db.OperationLog import OperationLog
from NationalEducationRadio.models.db.PlayLog import PlayLog
from NationalEducationRadio.models.db.HotPlay import HotPlay
from NationalEducationRadio.models.db.OperationLog import OperationLog
from NationalEducationRadio.models.db.TimeHotPlay import TimeHotPlay
from NationalEducationRadio.models.db.SearchLog import SearchLog
from NationalEducationRadio.models.db.SearchSelectedLog import SearchSelectedLog
from NationalEducationRadio.models.db.KeywordsTable import KeywordsTable
from NationalEducationRadio.models.recommend.batch import count_user_time_hot_play, similar_audio, hot_play, op_habit, timehotplay, keywordprocessing
from NationalEducationRadio.controllers.recommend import recommend_audios
from collections import OrderedDict
import jieba
import jieba.analyse
import requests
import numpy as np
import os
from hanziconv import HanziConv
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
from collections import Set

from flask_login import UserMixin, LoginManager, login_required, current_user, login_user, logout_user

root = get_blueprint('root')
radio = get_blueprint('radio')

@root.route('/', methods=['GET', ])
def root_index():
    return redirect(url_for('radio.index'))

# @radio.route('/test', methods=['GET', ])
# def knowledge_index():
#     print("test")
#     return render_template('radio/knowledge.html')


@radio.route('/', methods=['GET', ])
@login_required
def index():
    """
    首頁抓第一筆資訊並跳轉到那頁
    :return: 第一筆節目音檔的頁面
    """
    ado = Audio.query.first()
    return redirect(url_for('radio.show', channel_id=ado.audio_channel, audio_id=ado.audio_id))


@radio.app_errorhandler(404)
def handle_404(err):
    return request.path


@radio.route('/json/<int:channel_id>/<int:audio_id>', methods=['GET', ])
@login_required
def showJson(channel_id, audio_id):
    """
    將該音檔所帶有的資訊與題目轉換成 JSON，讓 React 使用
    :return: JSON 格式資訊
    """
    channel = Channel.query.filter_by(channel_id=channel_id).first()
    audios = Audio.query.filter_by(channel=channel).all()
    audio = Audio.query.filter_by(audio_id=audio_id).first()
    summary = get_solr_data(audio.audio_id)
    if audio is None or channel is None or audio.channel != channel:
        return "Nothing"

    """
    計算前後，有更好的方法嗎？
    """
    aI = 0
    now = None
    pre = None
    nxt = None
    for x in audios:
        if aI > 0 and now is None:
            pre = audios[aI - 1].audio_id
        if now is not None:
            nxt = audios[aI].audio_id
            break

        if x == audio:
            now = aI
        aI += 1

    a = [1, 2, 3, 4, 5, 6]
    json_content = {}
    json_content['channel_id'] = channel_id
    json_content['channel_name'] = channel.channel_name
    json_content['audio_id'] = audio_id
    json_content['audio_name'] = audio.audio_name
    json_content['audio'] = url_for('static', filename="upload/" + audio.audio_file)
    json_content['title'] = audio.audio_name
    json_content['depiction'] = audio.channel.channel_memo
    json_content['logo'] = url_for('static', filename="images/covers/" + str(random.choice(a)) + ".jpg")
    json_content['forward'] = url_for('radio.show', channel_id=channel_id, audio_id=nxt) if nxt is not None else "#"
    json_content['backward'] = url_for('radio.show', channel_id=channel_id, audio_id=pre) if pre is not None else "#"
    json_content['questions'] = json.loads(audio.audio_question)
    json_content['audio_summary'] = summary
    
    keyword = []
    if audio.keyword is not None:
        keyword = audio.keyword.split(",")

    json_content['keywords'] = keyword
    return json.dumps(json_content, ensure_ascii=False)


@radio.route('/login', methods=['GET', 'POST'])
def login():
    def login_redirect():
        return redirect(url_for('radio.index'))

    if current_user.is_anonymous is not True:
        return login_redirect()

    form = LoginForm()
    form2 = RegisterForm()
    if form.validate_on_submit():
        # new_user = User(name=form2.name.data,
        # 	account=form2.account.data,
        # 	password=password_encryption(form2.password.data),
        # 	level=0)
        # db.session.add(new_user)
        # db.session.commit()

        admin_user = User.query.filter_by(account=form.account.data,
                                          password=password_encryption(form.password.data)).first()
        print(admin_user)
        if admin_user is not None:
            session['level'] = admin_user.level
            login_user(admin_user)
            return login_redirect()
        else:
            flash('帳號或密碼錯誤')
    required_to_flash(form)
    return render_template('radio/login.html', current_user=current_user, form=form, reg=form2)


@radio.route('/error')
def accountExist():
    return "exist"


@radio.route('/message')
def message():
    return '''
        <script>
            alert("{message}");
            window.location="{location}"; 
        </script>'''.format(
        message=str(request.args['message']),
        location=request.args['location']
    )


@radio.route('/register', methods=['POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        (exist,), = db.session.query(exists().where(User.account == form.account.data))  # check account existance
        if (exist):
            return redirect(url_for('radio.message', message='帳號重複', location='login'))

        new_user = User(name=form.name.data,
                        account=form.account.data,
                        password=password_encryption(form.password.data),
                        level=0)

        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('radio.message', message='註冊成功，請重新登入', location='login'))
        # return render_template('radio/register.html', current_user=current_user, form=form)


@radio.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('radio.login'))


@radio.route('/dosomething', methods=['POST', ])
@login_required
def dosomething():
    audio = Audio.query.filter_by(audio_id=request.json['audio_id']).first()
    user = User.query.filter_by(id=current_user.id).first()
    record = Record(audio=audio, user=user, record_data=json.dumps(request.json['questions']))

    return "success"


@radio.route('/record', methods=['GET', 'POST'])
def record():
    # audios = Audio.query.filter_by(channel=channel).all()
    records = Record.query.filter_by(user_id=current_user.id).order_by(desc(Record.record_id)).all()
    return render_template('radio/record.html', current_user=current_user, records=records)


@radio.route('/view/<record_id>', methods=['GET', 'POST'])
def view(record_id):
    record = Record.query.filter_by(user_id=current_user.id, record_id=record_id).first()
    audio = record.audio
    questions = json.load(StringIO(audio.audio_question))
    for question in questions:
        question['user_answer'] = 0
        question['answer'] = 0

    recordData = json.load(StringIO(record.record_data))
    for data in recordData:
        for question in questions:
            if data['id'] == question['id']:
                question['user_answer'] = data['user_answer']
                question['answer'] = data['answer'][0]
                break

    return render_template('radio/view.html', questions=questions)


@radio.route('/<int:channel_id>/<int:audio_id>/', methods=['GET', ])
@login_required
def show(channel_id, audio_id):
    nextChannel = Channel.query.join(Audio, Audio.audio_channel == Channel.channel_id).filter(
        Channel.channel_id > channel_id).first()
    if nextChannel is not None:
        nextAudio = Audio.query.filter_by(audio_channel=nextChannel.channel_id).first()
    else:
        nextAudio = None
    audio = Audio.query.filter_by(audio_id=audio_id).first()
    audios = Audio.query.filter_by(audio_channel=channel_id).order_by(Audio.audio_id).all()
    success, keywords, summary = get_solr_data(audio.audio_id)
    if success is False:
        summary = audio.channel.channel_memo
    else:
        keywords = keywords.split(" , ")

    recommend_audio = recommend_audios(current_user.id, audio_id)
    print(recommend_audio)
    return render_template('radio/front_index.html', targetAudio=audio, audios=audios, recommend_audio = recommend_audio, nextChannel=nextChannel,
                           nextAudio=nextAudio,
                           success=success, summary=summary, keywords=keywords, page="show",
                           json_file=url_for('radio.showJson', channel_id=channel_id, audio_id=audio_id))


@radio.route('/newIndex', methods=['GET', ])
@login_required
def newIndex():
    """
    首頁抓第一筆資訊並跳轉到那頁
    :return: 第一筆節目音檔的頁面
    """
    ado = Audio.query.group_by(Audio.audio_channel).first()
    return redirect(url_for('radio.show', channel_id=ado.audio_channel, audio_id=ado.audio_id))


@radio.route('/front_record', methods=['GET', ])
def front_record():
    records = Record.query.filter_by(user_id=current_user.id).order_by(desc(Record.record_id)).all()
    ids = list()
    for record in records:
        ids.append(record.audio.audio_channel)

    channels = Channel.query.filter(Channel.channel_id.in_(set(ids))).all()

    session1 = []
    session2 = []
    for channel in channels:
        session1.append({
            'channel_id': channel.channel_id,
            'name': channel.channel_name,
            'count': ids.count(channel.channel_id)
        })
        for record in records:
            audio = record.audio
            if audio.audio_channel == channel.channel_id:
                questions = json.load(StringIO(audio.audio_question))
                for question in questions:
                    question['user_answer'] = 0
                    question['answer'] = 0

                recordData = json.load(StringIO(record.record_data))
                for data in recordData:
                    for question in questions:
                        if data['id'] == question['id']:
                            question['user_answer'] = data['user_answer']
                            question['answer'] = data['answer'][0]
                            break
                session2.append((record, questions))

    return render_template('radio/front_record.html', session1=session1, session2=session2, page="record")

# ***
@radio.route('/get_playlog', methods=['POST',])
@login_required
def get_playlog():  
    ts = int(time.time())
    Pl = PlayLog(
        audio = request.json['audio_id'], 
        user = current_user.id,
        star_time = ts)
    db.session.add(Pl)
    db.session.commit()

    playlog_id = PlayLog.query.filter_by(user = current_user.id).order_by(desc(PlayLog.play_log_id)).first()
    json_content = {}
    json_content['playlog_id'] = playlog_id.play_log_id

    return json.dumps(json_content, ensure_ascii=False)
# ***

@radio.route('/add_playlog_end_time', methods=['POST',])
@login_required
def add_playlog_end_time():  
    ts = int(time.time())
    #print(ts)
    #print(request.json['playLogId'])
    playlog = PlayLog.query.filter_by(play_log_id = request.json['playLogId']).first()
    playlog.end_time = ts
    db.session.commit()

    return "success"

# ***
@radio.route('/add_oplog', methods=['POST',])
@login_required
def add_oplog():
    ts = int(time.time())
    Op = OperationLog(
        play_log = request.json['play_log'],
        operation_code = request.json['operation_code'],
        operation_value = request.json['operation_value'],
        timestamp = ts)
    db.session.add(Op)
    db.session.commit()

    return "success"

@radio.route('/get_new_audio_id', methods=['POST',])
@login_required
def get_new_audio_id():  
    ret = ""
    audio = Audio.query.with_entities(Audio.audio_id).all()
    if request.json['button_type'] == "forward" :
        for i in range(len(audio)):
            if audio[i][0] == request.json['audio_id'] and i+1 <= len(audio):
                ret = str(audio[i+1][0])
    elif request.json['button_type'] == "backward" :
        for i in (range(len(audio)), -1, -1):
            if audio[i][0] == request.json['audio_id'] and i-1 >= 0:
                ret = str(audio[i-1][0])
    else:
        pass
    json_content = {}
    json_content['audio_id'] = request.json['audio_id']
    ###############
    return json.dumps(json_content, ensure_ascii=False)


@radio.route('/daily_batch/', methods=['GET', ])
def daily_batch():

    #每日例行批次計算

    print("****** Start processing Daily_batch ! ******\n", file=sys.stderr)
    #全系統
    keywordprocessing()
    similar_audio()
    hot_play()
    timehotplay()
    #全部使用者
    users = User.query.all()
    print("****** Start processing count_user_time_hot_play Module ! ******\n", file=sys.stderr)
    for user in users:
       count_user_time_hot_play(user.id)
    print("****** Processing count_user_time_hot_play Module done ! ******\n", file=sys.stderr)

    # print("****** Start processing op_habit ! ******\n", file=sys.stderr)
    for user in users:
       op_habit(user.id)
    # print("****** Processing op_habit done! ******\n", file=sys.stderr)

    print("****** Processing Daily_batch done! ******\n", file=sys.stderr)

    return "Processing Daily_batch done!"

@radio.route('/API_FB_login', methods=['POST'])
def API_FB_login():
    userID = request.json['userID']
    accessToken = request.json['accessToken']
    userName = request.json['userName']
    userEmail = request.json['userEmail']
    print(userID, accessToken, userName, userEmail)
    FBuserID_Exist = User.query.filter_by(FBuserID=userID).first()
    if FBuserID_Exist == None:
        newAccount = User(name=userName,
                          account=userEmail,
                          password=None,
                          level=123,
                          FBuserID=userID,
                          FBAccessToken=accessToken)
        db.session.add(newAccount)
        login_user(newAccount)
    else:
        FBuserID_Exist.FBAccessToken = accessToken
        db.session.add(FBuserID_Exist)
        login_user(FBuserID_Exist)
    db.session.commit()
    
    return '11'

@radio.route('/API_GOOGLE_login', methods=['POST'])
def API_GOOGLE_login():
    userID = request.json['userID']
    userName = request.json['userName']
    userEmail = request.json['userEmail']
    print(userID, userName, userEmail)
    GOOGLEuserID_Exist = User.query.filter_by(GOOGLEuserID=userID).first()
    if GOOGLEuserID_Exist == None:
        newAccount = User(name=userName,
                          account=userEmail,
                          password=None,
                          level=123,
                          GOOGLEuserID=userID)
        db.session.add(newAccount)
        login_user(newAccount)
    else:
        db.session.add(GOOGLEuserID_Exist)
        login_user(GOOGLEuserID_Exist)
    db.session.commit()
    
    return '11'

# need to change keyword search
@radio.route('/knowledge', methods=['GET', ])
def knowledge():
    finalResult = []
    # get search keyword
    keyword = str(request.args.get('search'))
    #keyword = "廣播"
    # scrawler setting
    # url = "http://140.124.183.5:8983/solr/EBCStation/select?indent=on&q=*:*&rows=999&wt=json"
    # url = "http://nermoocs.org/solr/EBCStation/select?indent=on&q=*:*&rows=999&wt=json"
    url = "http://127.0.0.1/solr/EBCStation/select?indent=on&q=*:*&rows=999&wt=json"
    article = requests.get(url).json()
    # db length
    articleLen = article['response']['numFound']
    # save audio_id
    audioID = set()
    # filter Audio ID
    for a in range(articleLen):
        if len(audioID) is 100:
            break
        if keyword in article['response']['docs'][a]['content']:
            audioID.add(article['response']['docs'][a]['audio_id'])
    print(audioID)
    # query Audio Info from db
    for i in audioID:
        # save one audio format result
        result = {}
        audioInfo = Audio.query.filter_by(audio_id=i).first()
        if audioInfo is None:
            continue
        result["id"] = i
        # processing keyword string format
        keywordList = []
        if audioInfo.keyword is not None:
            for k in HanziConv.toTraditional(audioInfo.keyword).split(","):
                if k is not '':
                    keywordList.append(k)
        # save json format parameters
        result["keyWord"] = keywordList
        result["type"] = audioInfo.audio_channel
        result["title"] = audioInfo.audio_name
        result["text"] = ""
        # get similar audio ID
        similarAudioData = Audio.query.filter_by(audio_id=i).first().similar_audio
        # save ID
        similarAudioID = []
        # str covert to dict
        if similarAudioData is not None:
            listSimilarAudio = ast.literal_eval(similarAudioData)
            # save audio all similarAudioID
            for l in listSimilarAudio:
                for k in l.keys():
                    similarAudioID.append(int(k))
        result["links"] = similarAudioID
        finalResult.append(result)

    print(finalResult)

    resp = Response(response=json.dumps(finalResult, ensure_ascii=False),
                    status=200,
                    mimetype="application/json")

    return resp


# caption get
@radio.route('/captionGet', methods=['POST', ])
def captionGet():
    # scrawler setting
    url = "http://127.0.0.1/solr/EBCStationCaption/select?indent=on&q=*:*&rows=9999&wt=json"
    # url = "http://nermoocs.org/solr/EBCStationCaption/select?indent=on&q=*:*&rows=9999&wt=json"
    caption = requests.get(url).json()
    # db length
    captionLen = caption['response']['numFound']
    audio_id = request.json['audio_id']
    print(audio_id)
    for l in range(captionLen):
        captionList = []
        if caption['response']['docs'][l]['audio_id'] == audio_id:
            for i in caption['response']['docs'][l]['caption'].split("\n"):
                content = i.split(",")
                if len(content) < 2:
                    continue
                captionList.append({
                'start_time': content[0],
                'end_time': content[1],
                'caption': content[2]
                })
            break
    print(captionList)
    return json.dumps(captionList, ensure_ascii=False)
