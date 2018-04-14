# -*- coding: utf-8 -*-
import time
import sys
import math
import random
import json
from io import StringIO
from datetime import datetime, timedelta
from flask import Flask, redirect, url_for, render_template, session, flash, request, jsonify
from flask.ext.login import current_user, login_required, logout_user, login_user
from sqlalchemy import desc
from sqlalchemy import exists

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


radio = get_blueprint('radio')


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
    return render_template('radio/front_index.html', targetAudio=audio, audios=audios, nextChannel=nextChannel,
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


# searchselect
@radio.route('/searchselect', methods=['GET', ])
def searchselect():
    # setting query string
    queryString = "education"
    # query all similar keywords data from SearchLog db
    searchLogdb = SearchLog.query.filter(SearchLog.search_text.ilike("%" + queryString + "%")).all()

    # using search_id to link SearchSelectedLog db
    # calculate audio rank
    # initial parameters, rankTanble : save audio count rank
    rankTable = {}
    # iteration for query all similar keywords
    for i in range(len(searchLogdb)):
        # get search_id from SearchLogdb
        searchLogdbId = searchLogdb[i].search_id
        # query search_id from SearchSelectedLog db by search_id
        searchSelectLogdb = SearchSelectedLog.query.filter_by(search_id=searchLogdbId)
        # get audioId from SearchSelectedLog
        audioId = searchSelectLogdb[0].audio
        # calculate audio count
        # must be initialized rankTable first if audioId not store on rankTable
        # otherwise count plus one
        if audioId not in rankTable:
            rankTable[audioId] = 1
        else:
            rankTable[audioId] += 1
    # sorting attribute count on rankTable by using OrderedDict
    # output from largest to smallest
    OrderedRankTable = OrderedDict(sorted(rankTable.items(), key=lambda t: t[1], reverse=True))
    return json.dumps(OrderedRankTable)


# searchkeywords
@radio.route('/searchkeywords', methods=['GET', ])
def searchkeywords():
    # setting query string and my user id
    queryString = "education"
    myUserId = 1
    # query all search similar keywords data from SearchLog db
    searchLogdb = SearchLog.query.filter(SearchLog.search_text.ilike("%" + queryString + "%")).all()
    # get all search similar keywords user
    similarUser = []
    for i in range(len(searchLogdb)):
        if searchLogdb[i].user not in similarUser:
            similarUser.append(searchLogdb[i].user)
    # remove myUserid from all search similar keywords user
    similarUser.remove(myUserId)

    # use search similar keywords user to calculatedly watch audio count from PlayLog db
    audioWatchRank = {}
    for i in range(len(similarUser)):
        # filter user information from PlayLog db by user id each time
        oneUserWatchAudio = PlayLog.query.filter_by(user=similarUser[i]).all()
        # get one user have seen audio
        for j in range(len(oneUserWatchAudio)):
            audioId = oneUserWatchAudio[j].audio
            if audioId not in audioWatchRank:
                audioWatchRank[audioId] = 1
            else:
                audioWatchRank[audioId] += 1
    # sorting attribute audio count on audioWatchRank by using OrderedDict
    # output from largest to smallest
    OrderedRankTable = OrderedDict(sorted(audioWatchRank.items(), key=lambda t: t[1], reverse=True))
    return json.dumps(OrderedRankTable)


# keywordprocessing
@radio.route('/keywordprocessing', methods=['GET', ])
def keywordprocessing():

    # ******** scrawler, get all article ********
    url = "http://140.124.183.5:8983/solr/EBCStation/select?indent=on&q=*:*&rows=300&wt=json"
    article = requests.get(url).json()
    articleLen = 281

    # ******** load Jieba setting ********
    _resultDir = os.path.dirname(os.path.abspath(__file__)) + '/'
    jieba.analyse.set_stop_words(_resultDir + 'dict_stop_words.txt')
    jieba.set_dictionary(_resultDir + 'dict.txt.big')
    jieba.load_userdict(_resultDir + 'stopwords.txt')

    # ******** calculate TF-IDF Start ********

    # done TF-IDF value calculate

    corpus = []
    for i in range(articleLen):
        content = article['response']['docs'][i]['content']
        Simpcontent = HanziConv.toSimplified(content)
        js = json.dumps(Simpcontent, ensure_ascii=False)
        words = jieba.cut(js, cut_all=True)
        corpus.append(" ".join(words))

    Top10alllist = dict()  # 儲存每則文的keywords

    # update final tf_idf table
    def addNumber(name, number):
        if name in Top10alllist:
            if Top10alllist[name] < number:
                Top10alllist[name] = number
        else:
            Top10alllist[name] = number

    # tf_idf API
    countvec = CountVectorizer()  # ????文本中的???????矩?，矩?元素a[i][j] 表示j?在i?文本下的??
    trans = TfidfTransformer()  # ?????每???的tf-idf?值

    wordFrequence = countvec.fit_transform(corpus)
    tfidf = trans.fit_transform(wordFrequence)  # 第一?fit_transform是?算tf-idf，第二?fit_transform是?文本????矩?

    words = countvec.get_feature_names()  # ?取?袋模型中的所有??
    Weight = tfidf.toarray()  # ?tf-idf矩?抽取出?，元素a[i][j]表示j?在i?文本中的tf-idf?重

    # update td_idf table
    for weight in Weight:
        loc = np.argsort(-weight)  # 將weight降序排列也就是由大到小排列
        for i in range(len(weight)):  # 每篇文章all keywords的tfidf值當作代表
            tmp1 = words[loc[i]]
            tmp2 = weight[loc[i]]
            addNumber(tmp1, tmp2)

    # sort tf_idf table
    result = sorted(Top10alllist.items(), key=lambda Top10alllist: Top10alllist[1], reverse=True)

    # ******** calculate TF-IDF End ********


    # ******** relation Table processing Start ********
    
    # done relation table create 
    
    # clear relation table
    cleardb = db.session.query(KeywordsTable).delete()
    db.session.commit()

    # relation table create
    keyword_size = 100
    # initial keywordAmount table for store result
    keywordAmount = np.zeros((keyword_size, keyword_size), int)
    # create relation table co-occurrence
    for i in range(articleLen):
        content = article['response']['docs'][i]['content']
        Simpcontent = HanziConv.toSimplified(content)
        for j in range(100):
            if result[j][0] in content:
                for k in range(100):
                    if j == k:
                        continue
                    if result[k][0] in content:
                        keywordAmount[j][k] += 1

    keywords_id = 1
    for i in range(100):
        for j in range(100):
            if i != j:
                keywordA = result[i][0]
                keywordB = result[j][0]
                db.session.add(
                    KeywordsTable(keywords_id=keywords_id, keyword1=keywordA, keyword2=keywordB, count=int(keywordAmount[i][j])))
                keywords_id += 1
        db.session.commit()

    # ******** relation Table processing End ********


    # ******** audio keyword processing Start ********

    # done audio keyword save

    # audio keyword threshold value
    keywordParameter = 0.385
    for i in range(4):
        j = i+1
        content = article['response']['docs'][i]['content']
        Simpcontent = HanziConv.toSimplified(content)
        audioKeyword = ""
        rawKeyword = ""
        # filter keyword appear in audio and tf-idf value bigger than threshold value
        for r in range(100):
                if result[r][0] in Simpcontent:
                    rawKeyword += result[r][0] + ","
                    if result[r][1] > keywordParameter:
                        audioKeyword += result[r][0] + ","
        # get first audio data information filter by audio id, for update audio keyword
        audioData = Audio.query.filter_by(audio_id=j).first()
        # update keyword , using string to avoid save error
        audioData.keyword = str(audioKeyword)
        # update raw_keyword , using string to avoid save error
        audioData.raw_keyword = str(rawKeyword)
        db.session.commit()

    return str("keywordProcessing Done!")
    # ******** audio keyword processing End ********

# relationkeyword
@radio.route('/relationkeyword', methods=['GET', ])
def relationkeyword():

    # ******** get user highest watch audio Id Start ********
    queryUserId = 1
    # filter all watch audio Id on one user
    userPlayLog = PlayLog.query.filter_by(user=queryUserId).all()
    rankTable = {}
    # retrieval all watch audio ont one user
    for i in range(len(userPlayLog)):
        audioId = userPlayLog[i].audio
        # calculate audio count
        # must be initialized rankTable first if audioId not store on rankTable,otherwise count plus one
        if audioId not in rankTable:
            rankTable[audioId] = 1
        else:
            rankTable[audioId] += 1
    # sorting attribute count on rankTable by using OrderedDict, output from largest to smallest
    OrderedRankTable = OrderedDict(sorted(rankTable.items(), key=lambda t: t[1], reverse=True))

    # ******** get user highest watch audio Id End ********


    # ******** create relationkeywordset Start ********

    # query top k rank audio
    queryFlag = 2
    # record my top k watch audio id
    topAudioId = set()
    # save all relation keyword by top k rank audio
    relationKeywordSet = set()
    for i in range(queryFlag):
        # get highest rank audio id by sorted RankTable
        highestAudioId = list(OrderedRankTable.items())[i]
        # get audio keyword by audio id
        getkeyword = Audio.query.filter_by(audio_id=highestAudioId[0]).first().keyword
        # split "," on Db
        splitList = getkeyword.split(",")
        for j in splitList:
            if j is not '':
                relationKeywordSet.add(j)
        topAudioId.add(highestAudioId[0])
    # ******** create relationkeywordset End ********


    # ******** Final audio recommendation by relationkeyword Start ********
    audioDbLen = Audio.query.count()
    # retrieval all watch audio expect top k rank audio
    for i in range(1, audioDbLen+1):
        AudioId = i
        # exclude user top k audio
        if AudioId not in topAudioId:
            # get audio keyword by audio id
            getkeyword = Audio.query.filter_by(audio_id=AudioId).first().keyword
            # for calculate audio keyword appear count
            audioCount = 0
            # split "," on Db
            splitList = getkeyword.split(",")
            for j in splitList:
                # if keyword appear both on relation keyword set and article, then this audio count plus one
                if j in relationKeywordSet:
                    audioCount += 1
            # for sorting all audio count rank
            audioRankTable = {}
            if AudioId not in audioRankTable:
                audioRankTable[AudioId] = audioCount
            else:
                return str("Error occur!")
    # sorting attribute count on rankTable by using OrderedDict, output from largest to smallest
    finalAudioCountTable = OrderedDict(sorted(audioRankTable.items(), key=lambda t: t[1], reverse=True))
    # ******** Final audio recommendation by relationkeyword End ********
    return json.dumps(finalAudioCountTable, ensure_ascii=False)


@radio.route('/usertimehotplay/<int:user_id>', methods=['GET', ])
def usertimehotplay(user_id):
    """
    取得使用者最常使用時段的時段推薦
    """
    user = User.query.filter_by(id=user_id).first()
    time_hot_plays = TimeHotPlay.query.filter_by(time_zone=user.most_use_time).all()
    result = []
    for time_hot_plauy in time_hot_plays:
        result.append({
            "audio_id": time_hot_plauy.audio.audio_id,
            "audio_name": time_hot_plauy.audio.audio_name,
            "audio_channel": time_hot_plauy.audio.audio_channel
        })
    return json.dumps(result, ensure_ascii=False)


@radio.route('/daily_batch/', methods=['GET', ])
def daily_batch():

    #每日例行批次計算

    print("****** Start processing Daily_batch ! ******\n", file=sys.stderr)
    #全系統
    #keywordprocessing()
    #similar_audio()
    #hot_play()
    #timehotplay()
    #全部使用者
    users = User.query.all()
    print("****** Start processing count_user_time_hot_play Module ! ******\n", file=sys.stderr)
    #for user in users:
    #    count_user_time_hot_play(user.id)
    print("****** Processing count_user_time_hot_play Module done ! ******\n", file=sys.stderr)

    print("****** Start processing op_habit ! ******\n", file=sys.stderr)
    #for user in users:
    #    op_habit(user.id)
    print("****** Processing op_habit done! ******\n", file=sys.stderr)

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
