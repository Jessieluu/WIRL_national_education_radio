import time
import json
import sys
import operator

from NationalEducationRadio.service import db
from NationalEducationRadio.models.db.Audio import Audio
from NationalEducationRadio.models.db.User import User
from NationalEducationRadio.models.db.PlayLog import PlayLog
from NationalEducationRadio.models.db.TimeHotPlay import TimeHotPlay
from NationalEducationRadio.models.db.KeywordsTable import KeywordsTable
from NationalEducationRadio.models.db.OperationLog import OperationLog
from NationalEducationRadio.models.db.HotPlay import HotPlay


from collections import OrderedDict, Set
import jieba
import jieba.analyse
import requests
import numpy as np
import os
from hanziconv import HanziConv
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer

# done
def count_user_time_hot_play(queryUserId):
    """
    計算使用者最常收聽的時間
    """
    print("****** Start processing count_user_time_hot_play Module! ******\n", file=sys.stderr)
    dataSet = PlayLog.query.filter_by(user=queryUserId).all()
    morning = 0
    afternoon = 0
    evening = 0
    for i in range(len(dataSet)):
        timeStamp = int(dataSet[i].star_time)
        structTime = time.localtime(timeStamp)
        audioTime = structTime.tm_hour
        if audioTime >= 4 and audioTime < 11:
            morning += 1
        elif audioTime >= 11 and audioTime < 17:
            afternoon += 1
        elif audioTime >= 17 or audioTime < 4:
            evening += 1

    user = User.query.filter_by(id=queryUserId).first()
    if morning > afternoon and morning > evening:
        user.most_use_time = "morning"
    elif afternoon > morning and afternoon > evening:
        user.most_use_time = "afternoon"
    else:
        user.most_use_time = "evening"
    db.session.commit()
    print("****** Processing count_user_time_hot_play Module done! ******\n", file=sys.stderr)
# done
def similar_audio():
    """
    透過關鍵字取得相似節目
    """
    print("****** Start processing similar_audio Module! ******\n", file=sys.stderr)

    audios = Audio.query.all()
    for audio_x in audios:
        ranking = []
        if audio_x.keyword == "" or audio_x.keyword == None:
            continue

        for audio_y in audios:
            if audio_x.audio_id == audio_y.audio_id:
                continue
            if audio_y.keyword == "" or audio_y.keyword == None:
                continue
            #print(audio_x.keyword)
            keywords_x = audio_x.keyword.split(',')
            keywords_y = audio_y.keyword.split(',')
            keyword_counter = 0
            for kw_y in keywords_y:
                if kw_y in keywords_x:
                    keyword_counter = keyword_counter + 1
            ranking.append((audio_y.audio_id, keyword_counter))
        rnk = []
        tr = tuple(ranking)
        for key, value in tr:
            rnk.append({key: value})

        audio_x.similar_audio = json.dumps(rnk, ensure_ascii=False)
        db.session.commit()

    print("****** Processing similar_audio Module done! ******\n", file=sys.stderr)
    return True

# need to final, done
def hot_play():
    """
    熱門節目推薦模組
    """
    print("****** Start processing hot_play Module! ******\n", file=sys.stderr)
    playlog = PlayLog.query.order_by(PlayLog.audio).all()
    count = 0

    for i in range(len(playlog)):
        currentAudioId = playlog[i].audio 
        count += 1

        if i+1 < len(playlog) and currentAudioId is not playlog[i+1].audio or i+1 is len(playlog):
            HotPlay.query.filter_by(audio_id=currentAudioId).delete()
            db.session.add(HotPlay(audio_id=currentAudioId, count=count))
            count = 0
            db.session.commit()
    print("****** Processing hot_play Module done! ******\n", file=sys.stderr)

# need to final, done
def op_habit(queryUserId):
    """
    節目操作習慣推薦模組
    """
    print("****** Start processing op_habit Module! ******\n", file=sys.stderr)
    tmpStr = ""
    tmpCount = []
    playLog = PlayLog.query.filter_by(user=queryUserId).all() # Find the playlog list of `user` = 1

    for i in range(len(playLog)): # Traverse all the playlog
        # Use the `play_log_id` to find the corresponding opLog list 
        opLog = OperationLog.query.filter(OperationLog.play_log == playLog[i].play_log_id).all()   
        #Save the play_log and corresponding count
        tmpCount.append({
            'play_log' : playLog[i].play_log_id,
            'count' : len(opLog)
        })
    for i in range(0, len(tmpCount)-1):
        for j in range(0, len(tmpCount)-1-i):
            if tmpCount[j]['count'] < tmpCount[j+1]['count']:
                tmp = tmpCount[j]
                tmpCount[j] = tmpCount[j+1]
                tmpCount[j+1] = tmp


    for i in range(0, 4): 
        playLog_back = PlayLog.query.filter_by(play_log_id=tmpCount[i]['play_log']).first()
        tmpStr += str(playLog_back.audio) + ","

    playLog_back = PlayLog.query.filter_by(play_log_id=tmpCount[4]['play_log']).first()
    tmpStr += str(playLog_back.audio)
    user = User.query.filter_by(id=queryUserId).first()
    user.operation_ranks = tmpStr
    db.session.commit()
    print("****** Processing hot_play Module done! ******\n", file=sys.stderr)

# need to final, done
def timehotplay():

    print("****** Start processing timehotplay Module! ******\n", file=sys.stderr)
    # query all data from DB, order_by audio for process convenient
    dataSet = PlayLog.query.order_by(PlayLog.audio).all()
    # parameters initial
    morning = 0
    afternoon = 0
    evening = 0
    primaryId = 1
    for i in range(len(dataSet)):
        # take playLog information
        currentAudioId = dataSet[i].audio
        # partition time zone
        timeStamp = int(dataSet[i].star_time)
        structTime = time.localtime(timeStamp)
        audioTime = structTime.tm_hour
        if audioTime >= 4 and audioTime < 11:
            morning += 1
        elif audioTime >= 11 and audioTime < 17:
            afternoon += 1
        elif audioTime >= 17 or audioTime < 4:
            evening += 1

        # Condition description
        # when next audioID is not equal to currentAudioID, or iteration is end
        # both above do, delete information on DB by currentAudioId
        # then add parameters with AudioID information to DB
        if i + 1 < len(dataSet) and currentAudioId is not dataSet[i + 1].audio or i + 1 is len(dataSet):
            TimeHotPlay.query.filter_by(audio_id=currentAudioId).delete()
            db.session.add(TimeHotPlay(id=primaryId, audio_id=currentAudioId, count=morning, time_zone="morning"))
            primaryId += 1
            db.session.add(TimeHotPlay(id=primaryId, audio_id=currentAudioId, count=afternoon, time_zone="afternoon"))
            primaryId += 1
            db.session.add(TimeHotPlay(id=primaryId, audio_id=currentAudioId, count=evening, time_zone="evening"))
            primaryId += 1
            morning = 0
            afternoon = 0
            evening = 0

        db.session.commit()

    print("****** Processing hot_play Module done! ******\n", file=sys.stderr)

# done
def keywordprocessing():

    print("****** Start keywordProcessing Module! ******\n", file=sys.stderr)
    # ******** scrawler, get all article ********
    url = "http://140.124.183.5:8983/solr/EBCStation/select?indent=on&q=*:*&rows=300&wt=json"
    article = requests.get(url).json()
    # still need to find a way to getting all article length
    articleLen = article['response']['numFound']

    # ******** load Jieba setting ********
    _resultDir = os.path.dirname(os.path.abspath(__file__)) + '/'
    jieba.analyse.set_stop_words(_resultDir + 'dict_stop_words.txt')
    jieba.set_dictionary(_resultDir + 'dict.txt.big')
    jieba.load_userdict(_resultDir + 'stopwords.txt')


    # ******** calculate TF-IDF Start ********
    print("Starting calculated TF-IDF!\n", file=sys.stderr)
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
    print("Calculated TF-IDF done!\n", file=sys.stderr)
    # ******** calculate TF-IDF End ********

    # ******** relation Table processing Start ********
    print("Starting calculated relation Table!\n", file=sys.stderr)
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
    print("Calculated relation Table done!\n", file=sys.stderr)
    # ******** relation Table processing End ********


    # ******** audio keyword processing Start ********

    # audio keyword threshold value
    print("Starting calculated audio keyword!\n", file=sys.stderr)
    keywordParameter = 0.385
    for i in range(5):
        j = i+1
        content = article['response']['docs'][i]['content']
        Simpcontent = HanziConv.toSimplified(content)
        audioKeyword = ""
        rawKeyword = ""
        # filter keyword appear in audio and tf-idf value bigger than threshold value
        for r in range(100):
                if result[r][0] in Simpcontent:
                    rawKeyword += result[r][0] + ","
                    if result[r][1] >= keywordParameter:
                        audioKeyword += result[r][0] + ","
        # get first audio data information filter by audio id, for update audio keyword
        audioData = Audio.query.filter_by(audio_id=j).first()
        # update keyword , using string to avoid save error
        audioData.keyword = str(audioKeyword)
        # update raw_keyword , using string to avoid save error
        audioData.raw_keyword = str(rawKeyword)
        db.session.commit()
    print("Calculated audio keyword done!\n", file=sys.stderr)
    print("keywordProcessing Module Done!\n", file=sys.stderr)

    # ******** audio keyword processing End ********
